import { Telegraf } from "telegraf";

// Đặt token bot của bạn ở đây
const bot = new Telegraf("8456773993:AAEsp3fZLN7QogPDj6ggLEIhJFURshPMvHg");

// Khi user gõ /start
bot.start((ctx) => {
  ctx.reply("Xin chào 👋! Bot Telegram MiniApp đã hoạt động.");
});

// Một lệnh test khác
bot.command("hello", (ctx) => {
  ctx.reply("Hello world!");
});

// Luôn để ở cuối
bot.launch()
  .then(() => console.log("Bot is running 🚀"))
  .catch((err) => console.error("Error starting bot:", err));
