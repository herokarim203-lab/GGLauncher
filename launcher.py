import os
import sys
import json
import subprocess
import customtkinter as ctk
import minecraft_launcher_lib as mclib

# إعداد المظهر والثيم مسبقاً
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class GGLauncherPro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("GG Launcher PRO - Minecraft & Mods")
        self.geometry("550x500")
        self.resizable(False, False)

        # مسار ماين كرافت والملفات الافتراضية
        self.minecraft_dir = mclib.utils.get_minecraft_directory()
        self.config_file = os.path.join(self.minecraft_dir, "gg_launcher_config.json")
        
        # تحميل البيانات المحفوظة (الحسابات)
        self.config_data = self.load_config()

        # --- الواجهة الرسومية ---
        
        # العنوان
        self.title_label = ctk.CTkLabel(
            self, text="GG LAUNCHER PRO", font=ctk.CTkFont(size=26, weight="bold")
        )
        self.title_label.pack(pady=20)

        # إطار إدارة الحسابات
        self.account_frame = ctk.CTkFrame(self)
        self.account_frame.pack(pady=10, fill="x", px=20)

        self.acc_label = ctk.CTkLabel(self.account_frame, text="إدارة الحسابات:")
        self.acc_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # قائمة الحسابات المحفوظة
        self.account_option = ctk.CTkOptionMenu(
            self.account_frame, values=self.config_data.get("accounts", ["افتراضي"]), width=150
        )
        self.account_option.grid(row=1, column=0, padx=10, pady=5)

        # إضافة حساب جديد
        self.new_username_entry = ctk.CTkEntry(
            self.account_frame, placeholder_text="اسم حساب جديد...", width=150
        )
        self.new_username_entry.grid(row=1, column=1, padx=10, pady=5)

        self.add_acc_btn = ctk.CTkButton(
            self.account_frame, text="إضافة حساب ➕", width=100, command=self.add_account
        )
        self.add_acc_btn.grid(row=1, column=2, padx=10, pady=5)

        # إطار اختيار الإصدارات والمودات
        self.version_frame = ctk.CTkFrame(self)
        self.version_frame.pack(pady=15, fill="x", px=20)

        self.ver_label = ctk.CTkLabel(self.version_frame, text="اختر الإصدار أو محرك المودات (Forge/Fabric):")
        self.ver_label.pack(pady=5)

        # جلب الإصدارات والمودات المثبتة تلقائياً
        installed_versions = self.get_installed_versions()
        self.version_option = ctk.CTkOptionMenu(
            self.version_frame, values=installed_versions, width=300
        )
        self.version_option.pack(pady=5)

        # أزرار التحكم بالمودات والمجلدات
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.pack(pady=10)

        # زر فتح مجلد المودات
        self.mods_folder_btn = ctk.CTkButton(
            self.buttons_frame, 
            text="📁 فتح مجلد المودات (Mods)", 
            fg_color="#2c3e50", 
            hover_color="#34495e",
            command=self.open_mods_folder
        )
        self.mods_folder_btn.grid(row=0, column=0, padx=10)

        # زر فتح مجلد ماين كرافت الرئيسي (لتركيب المودباكات يدوياً)
        self.mc_folder_btn = ctk.CTkButton(
            self.buttons_frame, 
            text="🎮 مجلد اللعبة الرئيسي", 
            fg_color="#2c3e50", 
            hover_color="#34495e",
            command=self.open_minecraft_folder
        )
        self.mc_folder_btn.grid(row=0, column=1, padx=10)

        # زر تشغيل اللعبة الكبير
        self.play_button = ctk.CTkButton(
            self, 
            text="تشغيل اللعبة والمودات 🎮🔥", 
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#27ae60",
            hover_color="#2ecc71",
            command=self.launch_game,
            width=350,
            height=45
        )
        self.play_button.pack(pady=20)

        # شريط الحالة
        self.status_label = ctk.CTkLabel(self, text="جاهز للعب والمغامرة!", text_color="gray")
        self.status_label.pack(side="bottom", pady=10)

    # --- الدوال البرمجية لإدارة اللعبة ---

    def load_config(self):
        """تحميل الحسابات والإعدادات من ملف JSON"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {"accounts": ["Player1"]}

    def save_config(self, data):
        """حفظ الحسابات في ملف JSON"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_account(self):
        """إضافة حساب جديد إلى القائمة"""
        new_name = self.new_username_entry.get().strip()
        if new_name:
            accounts = self.config_data.get("accounts", [])
            if new_name not in accounts:
                accounts.append(new_name)
                self.config_data["accounts"] = accounts
                self.save_config(self.config_data)
                self.account_option.configure(values=accounts)
                self.account_option.set(new_name)
                self.new_username_entry.delete(0, "end")
                self.status_label.configure(text=f"✅ تم إضافة الحساب: {new_name}", text_color="green")
            else:
                self.status_label.configure(text="⚠️ الحساب موجود بالفعل!", text_color="yellow")

    def get_installed_versions(self):
        """جلب الإصدارات والمودات المثبتة تلقائياً"""
        try:
            versions = [v["id"] for v in mclib.utils.get_installed_versions(self.minecraft_dir)]
            if not versions:
                return ["1.20.1", "1.19.4", "1.16.5"]
            return versions
        except:
            return ["1.20.1", "1.19.4", "1.16.5"]

    def open_mods_folder(self):
        """فتح مجلد المودات مباشرة لوضع المودات والمودباكات فيه"""
        mods_path = os.path.join(self.minecraft_dir, "mods")
        os.makedirs(mods_path, exist_ok=True)
        os.startfile(mods_path)
        self.status_label.configure(text="📂 تم فتح مجلد المودات! ضع ملفات .jar للمودات هنا.")

    def open_minecraft_folder(self):
        """فتح مجلد ماين كرافت الرئيسي لتركيب المودباكات بالكامل"""
        os.startfile(self.minecraft_dir)
        self.status_label.configure(text="📂 تم فتح مجلد اللعبة الرئيسي.")

    def launch_game(self):
        username = self.account_option.get()
        selected_version = self.version_option.get()

        if not username or username == "افتراضي":
            self.status_label.configure(text="⚠️ يرجى اختيار حساب أو إضافة حساب جديد أولاً!", text_color="red")
            return

        self.status_label.configure(text=f"⏳ جاري التحقق وتشغيل {selected_version} للحساب {username}...", text_color="yellow")
        self.update_idletasks()

        options = {
            "username": username,
            "uuid": "",
            "token": ""
        }

        try:
            # إذا لم يكن الإصدار محلياً، نقوم بتحميله
            if not os.path.exists(os.path.join(self.minecraft_dir, "versions", selected_version)):
                self.status_label.configure(text="📥 جاري تحميل ملفات الإصدار الأساسية (قد يستغرق بعض الوقت)...")
                self.update_idletasks()
                mclib.install.install_minecraft_version(selected_version, self.minecraft_dir)

            # تشغيل اللعبة
            minecraft_command = mclib.command.get_minecraft_command(selected_version, self.minecraft_dir, options)
            subprocess.Popen(minecraft_command)
            self.destroy()
            sys.exit()

        except Exception as e:
            self.status_label.configure(text=f"❌ خطأ أثناء التشغيل: {str(e)}", text_color="red")

if __name__ == "__main__":
    app = GGLauncherPro()
    app.mainloop()
