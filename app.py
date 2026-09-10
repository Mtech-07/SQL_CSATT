import sys
import subprocess
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

ung_dung = Flask(__name__)
ung_dung.secret_key = 'sqli_lab_secret_key_2026'

CHE_DO_BAO_MAT = 'VULNERABLE' 

def lay_ket_noi_db():
    ket_noi = sqlite3.connect('database.db')
    ket_noi.row_factory = sqlite3.Row
    return ket_noi

def ghi_nhat_ky(diem_cuoi, du_lieu, trang_thai):
    ket_noi = lay_ket_noi_db()
    ket_noi.execute("INSERT INTO logs (endpoint, request_payload, status) VALUES (?, ?, ?)",
                 (diem_cuoi, str(du_lieu), trang_thai))
    ket_noi.commit()
    ket_noi.close()
    return True

@ung_dung.route('/')
def trang_chu():
    return redirect(url_for('dang_nhap'))

@ung_dung.route('/toggle-security', methods=['POST'])
def chuyen_doi_bao_mat():
    global CHE_DO_BAO_MAT
    CHE_DO_BAO_MAT = 'SECURE' if CHE_DO_BAO_MAT == 'VULNERABLE' else 'VULNERABLE'
    
    # Tu dong reset Database ve trang thai ban dau khi chuyen sang SECURE mode
    if CHE_DO_BAO_MAT == 'SECURE':
        try:
            subprocess.run([sys.executable, 'init_db.py'])
        except Exception as e:
            print("Loi reset Database:", e)

    return redirect(request.referrer or url_for('dang_nhap'))

@ung_dung.route('/login', methods=['GET', 'POST'])
def dang_nhap():
    loi_dang_nhap = None
    cau_lenh_sql = ""
    if request.method == 'POST':
        ten_dang_nhap = request.form['username']
        mat_khau = request.form['password']
        ket_noi = lay_ket_noi_db()
        con_tro = ket_noi.cursor()

        if CHE_DO_BAO_MAT == 'VULNERABLE':
            cau_lenh_sql = f"SELECT * FROM users WHERE username = '{ten_dang_nhap}' AND password = '{mat_khau}'"
            try:
                con_tro.executescript(cau_lenh_sql)
            except:
                pass
            
            try:
                nguoi_dung = con_tro.execute(cau_lenh_sql).fetchone()
            except Exception as e:
                nguoi_dung = None
                loi_dang_nhap = str(e)
        else:
            cau_lenh_sql = "SELECT * FROM users WHERE username = ? AND password = ?"
            nguoi_dung = con_tro.execute(cau_lenh_sql, (ten_dang_nhap, mat_khau)).fetchone()

        if nguoi_dung:
            session['logged_in'] = True
            session['username'] = nguoi_dung['username']
            session['role'] = nguoi_dung['role']
            ghi_nhat_ky('/login', f"User: {ten_dang_nhap}", "SUCCESS")
            return redirect(url_for('bang_dieu_khien'))
        else:
            if not loi_dang_nhap:
                loi_dang_nhap = "Thông tin đăng nhập không chính xác."
            ghi_nhat_ky('/login', f"User: {ten_dang_nhap}", "FAILED / SUSPICIOUS")

        ket_noi.close()

    return render_template('login.html', error=loi_dang_nhap, mode=CHE_DO_BAO_MAT, query=cau_lenh_sql)

@ung_dung.route('/dashboard')
def bang_dieu_khien():
    if not session.get('logged_in'):
        return redirect(url_for('dang_nhap'))
    return render_template('dashboard.html', username=session.get('username'), role=session.get('role'), mode=CHE_DO_BAO_MAT)

@ung_dung.route('/search', methods=['GET', 'POST'])
def tim_kiem():
    if not session.get('logged_in'):
        return redirect(url_for('dang_nhap'))

    danh_sach_ket_qua = []
    cau_lenh_sql = ""
    tu_khoa = ""

    if request.method == 'POST':
        tu_khoa = request.form['search']
        ket_noi = lay_ket_noi_db()
        con_tro = ket_noi.cursor()

        if CHE_DO_BAO_MAT == 'VULNERABLE':
            cau_lenh_sql = f"SELECT id, name, description, owner FROM records WHERE name LIKE '%{tu_khoa}%'"
            try:
                danh_sach_ket_qua = con_tro.execute(cau_lenh_sql).fetchall()
            except Exception as e:
                danh_sach_ket_qua = []
                cau_lenh_sql += f" ERROR: {str(e)}"
        else:
            cau_lenh_sql = "SELECT id, name, description, owner FROM records WHERE name LIKE ?"
            danh_sach_ket_qua = con_tro.execute(cau_lenh_sql, (f"%{tu_khoa}%",)).fetchall()

        ghi_nhat_ky('/search', tu_khoa, "SEARCH_PERFORMED")
        ket_noi.close()

    return render_template('search.html', results=danh_sach_ket_qua, mode=CHE_DO_BAO_MAT, query=cau_lenh_sql, search_term=tu_khoa)

@ung_dung.route('/manage', methods=['GET', 'POST'])
def quan_ly_du_lieu():
    if not session.get('logged_in'):
        return redirect(url_for('dang_nhap'))

    ket_noi = lay_ket_noi_db()
    con_tro = ket_noi.cursor()
    thong_bao_he_thong = None
    cau_lenh_sql = ""

    if request.method == 'POST':
        id_ban_ghi = request.form['id']
        mo_ta_moi = request.form['description']

        if CHE_DO_BAO_MAT == 'VULNERABLE':
            cau_lenh_sql = f"UPDATE records SET description = '{mo_ta_moi}' WHERE id = {id_ban_ghi}"
            try:
                con_tro.executescript(cau_lenh_sql)
                ket_noi.commit()
                thong_bao_he_thong = "Cập nhật thành công!"
            except Exception as e:
                thong_bao_he_thong = f"Lỗi: {str(e)}"
        else:
            cau_lenh_sql = "UPDATE records SET description = ? WHERE id = ?"
            try:
                con_tro.execute(cau_lenh_sql, (mo_ta_moi, id_ban_ghi))
                ket_noi.commit()
                thong_bao_he_thong = "Cập nhật thành công (Secure)!"
            except Exception as e:
                thong_bao_he_thong = f"Lỗi: {str(e)}"

        ghi_nhat_ky('/manage', f"ID: {id_ban_ghi}, Desc: {mo_ta_moi}", "MODIFY_ATTEMPT")

    tat_ca_ban_ghi = con_tro.execute("SELECT * FROM records").fetchall()
    ket_noi.close()

    return render_template('manage.html', records=tat_ca_ban_ghi, mode=CHE_DO_BAO_MAT, message=thong_bao_he_thong, query=cau_lenh_sql)

@ung_dung.route('/logs')
def xem_nhat_ky():
    if not session.get('logged_in'):
        return redirect(url_for('dang_nhap'))
    
    ket_noi = lay_ket_noi_db()
    du_lieu_nhat_ky = ket_noi.execute("SELECT * FROM logs ORDER BY id DESC").fetchall()
    ket_noi.close()
    return render_template('logs.html', logs=du_lieu_nhat_ky, mode=CHE_DO_BAO_MAT)

@ung_dung.route('/logout')
def dang_xuat():
    session.clear()
    return redirect(url_for('dang_nhap'))

if __name__ == '__main__':
    ung_dung.run(debug=True, port=5000)