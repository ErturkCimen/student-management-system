import sqlite3

DB_NAME = "students.db"


# ── VERİTABANI BAĞLANTISI ────────────────────────────────────────────────────

def get_connection():
    return sqlite3.connect(DB_NAME)


def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name       TEXT NOT NULL,
            student_number  TEXT UNIQUE NOT NULL,
            department      TEXT NOT NULL,
            grade           INTEGER NOT NULL,
            phone           TEXT
        )
    """)
    conn.commit()
    conn.close()


# ── CRUD FONKSİYONLARI ───────────────────────────────────────────────────────

def add_student(full_name, student_number, department, grade, phone):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO students (full_name, student_number, department, grade, phone)
            VALUES (?, ?, ?, ?, ?)
        """, (full_name, student_number, department, grade, phone))
        conn.commit()
        conn.close()
        print("\n✓ Öğrenci başarıyla eklendi.")
    except sqlite3.IntegrityError:
        print("\n✗ Bu öğrenci numarası zaten kayıtlı.")


def list_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, student_number, department, grade, phone FROM students ORDER BY student_number")
    students = cursor.fetchall()
    conn.close()

    if not students:
        print("\nHenüz kayıtlı öğrenci yok.")
        return

    print("\n" + "-" * 80)
    print(f"{'ID':<5} {'Ad Soyad':<22} {'Numara':<12} {'Bölüm':<25} {'Sınıf':<7} {'Telefon'}")
    print("-" * 80)
    for s in students:
        phone = s[5] if s[5] else "-"
        print(f"{s[0]:<5} {s[1]:<22} {s[2]:<12} {s[3]:<25} {s[4]:<7} {phone}")
    print("-" * 80)
    print(f"Toplam {len(students)} öğrenci listelendi.")


def search_student(student_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_number = ?", (student_number,))
    student = cursor.fetchone()
    conn.close()

    if student:
        print("\n--- Öğrenci Bilgileri ---")
        print(f"  ID           : {student[0]}")
        print(f"  Ad Soyad     : {student[1]}")
        print(f"  Numara       : {student[2]}")
        print(f"  Bölüm        : {student[3]}")
        print(f"  Sınıf        : {student[4]}")
        print(f"  Telefon      : {student[5] if student[5] else '-'}")
    else:
        print(f"\n✗ '{student_number}' numaralı öğrenci bulunamadı.")


def update_student(student_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_number = ?", (student_number,))
    student = cursor.fetchone()

    if not student:
        print(f"\n✗ '{student_number}' numaralı öğrenci bulunamadı.")
        conn.close()
        return

    print(f"\nGüncellenecek öğrenci: {student[1]}")
    print("Güncellemek istediğiniz alanı seçin:")
    print("  1 - Ad Soyad")
    print("  2 - Bölüm")
    print("  3 - Sınıf")
    print("  4 - Telefon")

    choice = input("Seçim: ").strip()

    field_map = {
        "1": ("full_name",  "Yeni Ad Soyad"),
        "2": ("department", "Yeni Bölüm"),
        "3": ("grade",      "Yeni Sınıf"),
        "4": ("phone",      "Yeni Telefon"),
    }

    if choice not in field_map:
        print("✗ Geçersiz seçim.")
        conn.close()
        return

    field, label = field_map[choice]
    new_value = input(f"{label}: ").strip()

    if not new_value:
        print("✗ Değer boş bırakılamaz.")
        conn.close()
        return

    if field == "grade":
        try:
            new_value = int(new_value)
        except ValueError:
            print("✗ Sınıf bilgisi sayı olmalıdır.")
            conn.close()
            return

    cursor.execute(f"UPDATE students SET {field} = ? WHERE student_number = ?",
                   (new_value, student_number))
    conn.commit()
    conn.close()
    print("\n✓ Öğrenci bilgisi güncellendi.")


def delete_student(student_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name FROM students WHERE student_number = ?", (student_number,))
    student = cursor.fetchone()

    if not student:
        print(f"\n✗ '{student_number}' numaralı öğrenci bulunamadı.")
        conn.close()
        return

    confirm = input(f"\n'{student[0]}' adlı öğrenciyi silmek istediğinize emin misiniz? (e/h): ").strip().lower()
    if confirm == "e":
        cursor.execute("DELETE FROM students WHERE student_number = ?", (student_number,))
        conn.commit()
        print("✓ Öğrenci silindi.")
    else:
        print("İşlem iptal edildi.")
    conn.close()


def show_statistics():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT department, COUNT(*) as count
        FROM students
        GROUP BY department
        ORDER BY count DESC
    """)
    by_dept = cursor.fetchall()

    cursor.execute("""
        SELECT grade, COUNT(*) as count
        FROM students
        GROUP BY grade
        ORDER BY grade
    """)
    by_grade = cursor.fetchall()

    conn.close()

    print("\n===== İSTATİSTİKLER =====")
    print(f"Toplam Öğrenci Sayısı : {total}")

    print("\nBölüme Göre Dağılım:")
    print("-" * 40)
    for dept, count in by_dept:
        print(f"  {dept:<30} {count} öğrenci")

    print("\nSınıfa Göre Dağılım:")
    print("-" * 40)
    for grade, count in by_grade:
        print(f"  {grade}. Sınıf{'':<24} {count} öğrenci")


# ── MENÜ ─────────────────────────────────────────────────────────────────────

def print_menu():
    print("\n" + "=" * 35)
    print("    ÖĞRENCİ YÖNETİM SİSTEMİ")
    print("=" * 35)
    print("  1 - Öğrenci Ekle")
    print("  2 - Öğrencileri Listele")
    print("  3 - Öğrenci Ara")
    print("  4 - Öğrenci Güncelle")
    print("  5 - Öğrenci Sil")
    print("  6 - İstatistikler")
    print("  0 - Çıkış")
    print("=" * 35)


def main():
    create_table()

    while True:
        print_menu()
        choice = input("Seçiminiz: ").strip()

        if choice == "1":
            print("\n--- Öğrenci Ekle ---")
            full_name      = input("Ad Soyad       : ").strip()
            student_number = input("Öğrenci Numarası: ").strip()
            department     = input("Bölüm          : ").strip()
            grade_input    = input("Sınıf (1-4)    : ").strip()
            phone          = input("Telefon (opsiyonel, boş bırakılabilir): ").strip()

            if not all([full_name, student_number, department, grade_input]):
                print("✗ Telefon dışındaki alanlar boş bırakılamaz.")
                continue

            try:
                grade = int(grade_input)
                if grade < 1 or grade > 4:
                    raise ValueError
            except ValueError:
                print("✗ Sınıf 1 ile 4 arasında bir sayı olmalıdır.")
                continue

            add_student(full_name, student_number, department, grade, phone or None)

        elif choice == "2":
            list_students()

        elif choice == "3":
            number = input("\nAranacak öğrenci numarası: ").strip()
            search_student(number)

        elif choice == "4":
            number = input("\nGüncellenecek öğrenci numarası: ").strip()
            update_student(number)

        elif choice == "5":
            number = input("\nSilinecek öğrenci numarası: ").strip()
            delete_student(number)

        elif choice == "6":
            show_statistics()

        elif choice == "0":
            print("\nProgramdan çıkılıyor. Görüşmek üzere!\n")
            break

        else:
            print("✗ Geçersiz seçim. Lütfen menüdeki numaralardan birini girin.")


if __name__ == "__main__":
    main()