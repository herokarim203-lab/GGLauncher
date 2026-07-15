import os
import sys
import requests
import customtkinter as ctk
import minecraft_launcher_lib as mclib
import subprocess

# إعداد المظهر والثيم مسبقاً لتفادي أي تعارض في ويندوز
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class GGLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()

        # إعدادات النافذة الرئيسية
        self.title("GG Launcher - Minecraft")
        self.geometry("450x350")
        self.resizable(False, False)

        # مسار ماين كرافت الافتراضي
        self.minecraft_dir = mclib.utils.get_minecraft_directory()

        # تصميم الواجهة (Widgets)
        self.title_label = ctk.CTkLabel(
            self, 
            text="GG LAUNCHER", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=25)

        # خانة اسم المستخدم
        self.username_entry = ctk.CTkEntry(
            self, 
            placeholder_text="اكتب اسمك هنا...", 
            width=250,
            justify="center"
        )
        self.username_entry.pack(pady=15)

        # قائمة اختيار إصدارات اللعبة
        self.version_label = ctk.CTkLabel(self, text="اختر الإصدار:")
        self.version_label.pack(pady=5)

        # جلب قائمة الإصدارات المتاحة
        installed_versions = self.get_installed_versions()
        self.version_option = ctk.CTkOptionMenu(
            self, 
            values=installed_versions, 
            width=180
        )
        self.version_option.pack(pady=5)

        # زر تشغيل اللعبة
        self.play_button = ctk.CTkButton(
            self, 
            text="تشغيل اللعبة 🎮", 
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.launch_game,
            width=200,
            height=40
        )
        self.play_button.pack(pady=30)

        # نص الحالة بالأسفل
        self.status_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.status_label.pack(side="bottom", pady=10)

    def get_installed_versions(self):
        """جلب الإصدارات المثبتة أو الافتراضية"""
        try:
            versions = [v["id"] for v in mclib.utils.get_installed_versions(self.minecraft_dir)]
            if not versions:
                return ["1.20.1", "1.19.4", "1.16.5"]
            return versions
        except Exception:
            return ["1.20.1", "1.19.4", "1.16.5"]

    def launch_game(self):
        username = self.username_entry.get().strip()
        selected_version = self.version_option.get()

        if not username:
            self.status_label.configure(text="⚠️ يرجى كتابة اسم المستخدم أولاً!", text_color="red")
            return

        self.status_label.configure(text="⏳ جاري تشغيل ماين كرافت...", text_color="yellow")
        self.update_idletasks()

        # إعدادات التشغيل الـ Offline مع إغلاق القوس بشكل صحيح ومضمون
        options = {
            "username": username,
            "uuid": "",
            "token": ""
        }

        try:
            # التحقق من وجود الإصدار محلياً، وإذا لم يكن موجوداً يتم تحميله
            if not os.path.exists(os.path.join(self.minecraft_dir, "versions", selected_version)):
                self.status_label.configure(text="📥 الإصدار غير مثبت، جاري التحميل (قد يستغرق بعض الوقت)...")
                self.update_idletasks()
                mclib.install.install_minecraft_version(selected_version, self.minecraft_dir)

            # جلب كود أمر تشغيل ماين كرافت
            minecraft_command = mclib.command.get_minecraft_command(selected_version, self.minecraft_dir, options)
            
            # تشغيل اللعبة في عملية منفصلة وإغلاق اللانشر
            subprocess.Popen(minecraft_command)
            self.destroy() 
            sys.exit()

        except Exception as e:
            self.status_label.configure(text=f"❌ خطأ أثناء التشغيل: {str(e)}", text_color="red")

if __name__ == "__main__":
    app = GGLauncher()
    app.mainloop()
