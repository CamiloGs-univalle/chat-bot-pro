// =============================================================
// PROSERVIS BOT - WhatsApp Gateway
// Archivo: whatsapp-gateway/index.js
//
// FUNCIÓN: Conectar el número de WhatsApp con el backend FastAPI.
//
// Flujo:
//   1. Conectar a WhatsApp vía Baileys (escanear QR)
//   2. Escuchar mensajes entrantes
//   3. Enviarlos al backend: POST http://127.0.0.1:8000/mensaje
//   4. Recibir la respuesta del bot
//   5. Enviarla de vuelta al usuario en WhatsApp
//
// INICIO:
//   cd whatsapp-gateway
//   node index.js
//
// Si el QR no aparece, borrar la carpeta sessions/ y reintentar.
// =============================================================

const axios  = require("axios");
const qrcode = require("qrcode-terminal");

const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason,
    fetchLatestBaileysVersion,
} = require("@whiskeysockets/baileys");


// ------------------------------------------------------------------
// CONFIGURACIÓN
// ------------------------------------------------------------------

const BACKEND_URL      = "http://127.0.0.1:8000/mensaje";  // URL del FastAPI
const SESSIONS_FOLDER  = "./sessions";                      // Carpeta de sesión WhatsApp
const RECONNECT_DELAY  = 3000;                              // ms antes de reconectar


// ------------------------------------------------------------------
// INICIAR EL BOT
// ------------------------------------------------------------------

async function iniciarBot() {
    // Cargar (o crear) las credenciales de sesión
    const { state, saveCreds } = await useMultiFileAuthState(SESSIONS_FOLDER);
    const { version }          = await fetchLatestBaileysVersion();

    console.log(`\n🚀 Iniciando Proservis Bot (Baileys v${version.join(".")})`);

    const sock = makeWASocket({
        version,
        auth:              state,
        printQRInTerminal: false,        // Lo mostramos nosotros con qrcode-terminal
        browser:           ["Proservis Bot", "Chrome", "1.0.0"],
        syncFullHistory:   false,        // Solo historial reciente
    });


    // ------------------------------------------------------------------
    // GUARDAR CREDENCIALES CUANDO SE ACTUALICEN
    // ------------------------------------------------------------------

    sock.ev.on("creds.update", saveCreds);


    // ------------------------------------------------------------------
    // MANEJAR CAMBIOS DE CONEXIÓN
    // ------------------------------------------------------------------

    sock.ev.on("connection.update", async (update) => {
        const { connection, lastDisconnect, qr } = update;

        // Mostrar QR para escanear con WhatsApp
        if (qr) {
            console.log("\n📱  ESCANEA ESTE CÓDIGO QR CON WHATSAPP:\n");
            qrcode.generate(qr, { small: true });
            console.log("\nPasos:\n  1. Abre WhatsApp en tu teléfono\n  2. Toca los tres puntos → 'Dispositivos vinculados'\n  3. 'Vincular un dispositivo'\n  4. Escanea este código\n");
        }

        // Conexión establecida
        if (connection === "open") {
            console.log("\n✅ WhatsApp conectado correctamente. El bot está activo.\n");
        }

        // Conexión cerrada
        if (connection === "close") {
            const statusCode = lastDisconnect?.error?.output?.statusCode;
            const sesionCerrada = statusCode === DisconnectReason.loggedOut;

            console.log(`\n⚠️  Conexión cerrada (código: ${statusCode})`);

            if (sesionCerrada) {
                // La sesión fue cerrada manualmente desde el teléfono
                console.log("❌  Sesión cerrada. Borra la carpeta 'sessions' y reinicia.");
            } else {
                // Error temporal → reconectar automáticamente
                console.log(`🔄  Reconectando en ${RECONNECT_DELAY / 1000} segundos...`);
                setTimeout(iniciarBot, RECONNECT_DELAY);
            }
        }
    });


    // ------------------------------------------------------------------
    // PROCESAR MENSAJES ENTRANTES
    // ------------------------------------------------------------------

    sock.ev.on("messages.upsert", async ({ messages, type }) => {
        // Solo procesar mensajes nuevos
        if (type !== "notify") return;

        const msg = messages[0];

        // Ignorar si no hay contenido o si es nuestro propio mensaje
        if (!msg.message) return;
        if (msg.key.fromMe) return;

        // Extraer el texto del mensaje (puede venir en diferentes estructuras)
        const texto = (
            msg.message.conversation                          ||
            msg.message.extendedTextMessage?.text            ||
            msg.message.imageMessage?.caption                ||
            msg.message.documentMessage?.caption             ||
            ""
        ).trim();

        // Ignorar mensajes vacíos (stickers, audios sin transcripción, etc.)
        if (!texto) {
            console.log("⏭️  Mensaje sin texto ignorado.");
            return;
        }

        // Obtener el número del remitente (quitar el @s.whatsapp.net)
        const telefono = msg.key.remoteJid.replace("@s.whatsapp.net", "");

        console.log(`\n📩  [${telefono}] → "${texto}"`);

        try {
            // Enviar al backend FastAPI
            const respuesta = await axios.post(
                BACKEND_URL,
                { telefono, mensaje: texto },
                { timeout: 15000 }   // 15 segundos máximo de espera
            );

            const textoRespuesta = respuesta.data.respuesta;

            // Enviar respuesta al usuario en WhatsApp
            await sock.sendMessage(
                msg.key.remoteJid,
                { text: textoRespuesta }
            );

            console.log(`🤖  [${respuesta.data.intencion}] ← "${textoRespuesta.substring(0, 80)}..."`);

        } catch (error) {
            // Log detallado del error
            if (error.response) {
                // El backend respondió con error HTTP
                console.error(`❌  Error del backend (${error.response.status}):`, error.response.data);
            } else if (error.code === "ECONNREFUSED") {
                // El backend no está corriendo
                console.error("❌  No se pudo conectar al backend. ¿Está corriendo FastAPI en el puerto 8000?");
            } else {
                console.error("❌  Error inesperado:", error.message);
            }

            // Enviar mensaje de error genérico al usuario
            try {
                await sock.sendMessage(
                    msg.key.remoteJid,
                    { text: "Lo siento, tuve un problema técnico. Intenta de nuevo en un momento. 🙏" }
                );
            } catch (sendError) {
                console.error("❌  No se pudo enviar el mensaje de error:", sendError.message);
            }
        }
    });
}


// ------------------------------------------------------------------
// INICIAR
// ------------------------------------------------------------------

iniciarBot().catch(err => {
    console.error("❌  Error fatal al iniciar el bot:", err);
    process.exit(1);
});