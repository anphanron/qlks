import math
from flask import render_template, request, redirect, flash, url_for
from app._init_ import login, app
from flask_login import login_user, logout_user, current_user
from datetime import date
from app.models import *
import dao
import hashlib

@app.route('/')
def index():
    kw = request.args.get('kw')
    pricefrom = request.args.get('pricefrom')
    priceto = request.args.get('priceto')
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1

    type_id = request.args.get('type_id')
    rooms = dao.load_rooms(kw=kw, type_id=type_id, pricefrom=pricefrom, priceto=priceto, page=page)
    total = dao.count_room()

    return render_template('index.html', rooms=rooms, pages=math.ceil(total / app.config['PAGE_SIZE']))


@app.route('/room/<id>')
def details(id):
    return render_template('xemPhong.html', room=dao.get_room_by_id(id))


@app.route('/admin/login', methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')

    user = dao.auth_user(username=username, password=password)
    if user:
        login_user(user=user)

    return redirect('/admin')


@app.route("/login/signup", methods=['post'])
def signup():
    err_msg = ""
    username = request.form.get('username')
    password = request.form.get('password')
    name = request.form.get('name')
    address = request.form.get('address')
    phone = request.form.get('phone')
    email = request.form.get('email')
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    check = NguoiDung.query.filter(NguoiDung.tenDangNhap.contains(username)).first()
    if check:
        err_msg = "Tài khoản đã tồn tại!"
        return render_template('dangNhap.html', err_msg=err_msg)
    else:
        c = NguoiDung(tenDangNhap=username, matKhau=password, hoTen=name, diaChi=address, soDT=phone, email=email, loaiNguoiDung = LoaiNguoiDung.KHACHHANG)
        db.session.add(c)
        db.session.commit()
        return redirect("/login")


@app.route("/login/signin", methods=['post'])
def signin():
    username = request.form.get('username')
    password = request.form.get('password')
    user = dao.auth_user(username, password)
    if user:
        login_user(user)
        return redirect("/")
    else:
        return redirect("/login")


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route("/login")
def login():
    return render_template('dangNhap.html')


@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect('/')


@app.route('/booking', methods=['GET', 'POST'])
def book_room():
    room_id = request.args.get('room_id') or request.form.get('room_id')

    room = None
    if room_id:
        room = dao.get_room_by_id(room_id)

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash("Vui lòng đăng nhập để tiếp tục", "warning")
            return redirect(url_for('login'))

        ngayNhan = request.form.get('check-in')
        ngayTra = request.form.get('check-out')
        count = int(request.form.get('count'))
        typeroom = request.form.get('type-room')

        print(f"ngayNhan: {ngayNhan}")
        print(f"ngayTra: {ngayTra}")
        print(f"count: {count}")
        print(f"typeroom: {typeroom}")

        khach_hang_id = current_user.khachhang.maKH if hasattr(current_user, 'khachhang') and current_user.khachhang else None
        print(f"khach_hang_id: {khach_hang_id}")

        if khach_hang_id is None:
            flash("Lỗi: Không tìm thấy thông tin khách hàng.", "error")
            return redirect(url_for('index'))  # Hoặc xử lý lỗi theo cách khác

        available_rooms = dao.get_available_rooms(typeroom, ngayNhan)
        print(f"available_rooms: {available_rooms}")
        if not available_rooms:
            flash(f"Không có phòng trống loại '{typeroom}' vào ngày {ngayNhan}.", "error")
            # Truyền typeroom vào lại template nếu không có phòng trống
            return render_template('datPhong.html', room=room, typeroom=dao.load_typeroom())

        selected_room = available_rooms[0]
        print(f"selected_room: {selected_room}")

        dat_phong = DatPhong(khachHang_id=khach_hang_id, ngayNhan=ngayNhan, ngayTra=ngayTra)
        print(f"dat_phong: {dat_phong}")

        dat_phong.phongs.append(selected_room)

        db.session.add(dat_phong)
        db.session.flush()
        print(f"dat_phong_id: {dat_phong.maDatPhong}")
        print(f"Dirty objects after adding dat_phong: {db.session.dirty}")

        # Tạo mới PhieuThuePhong và liên kết với DatPhong
        phieu_thue = PhieuThuePhong(datPhong_id=dat_phong.maDatPhong, ngayNhan=ngayNhan, ngayTra=ngayTra, soNguoi=count)
        print(f"phieu_thue: {phieu_thue}")
        phieu_thue.dsKhach.append(current_user.khachhang)
        db.session.add(phieu_thue)
        print(f"Dirty objects after adding phieu_thue: {db.session.dirty}")

        db.session.commit()
        print(f"Committed changes. Dirty objects: {db.session.dirty}")
        print(f"New objects: {db.session.new}")

        flash("Đặt phòng thành công!", "success")
        return redirect(url_for('index'))

    return render_template('datPhong.html', room=room, typeroom=dao.load_typeroom())


@app.route('/createform')
def create_form():
    return render_template('lapPhieu.html', roomform=dao.load_roomform())


@app.route('/createform/roomform/<id>')
def room_form(id):
    return render_template('phieuThue.html', roomform=dao.get_roomform_by_id(id))


@app.route('/createform/<id>')
def delete_form(id):
    roomform = LoaiPhong.query.get(id)
    if roomform:
        db.session.delete(roomform)
        db.session.commit()
        flash("Xóa phòng thành công!", "success")
    else:
        flash("Phòng không tồn tại!", "error")

    return redirect(url_for('create_form'))


@app.route('/pay')
def pay():
    roomform = dao.load_roomform()
    return render_template('thanhToan.html', roomform=roomform)


@app.route('/pay/delete/<id>')
def delete_bill(id):
    roomform = LoaiPhong.query.get(id)
    if roomform:
        db.session.delete(roomform)
        db.session.commit()
        flash("Xóa phòng thành công!", "success")
    else:
        flash("Phòng không tồn tại!", "error")

    return redirect(url_for('pay'))


@app.route('/pay/bill/<id>', methods=['GET','POST'])
def bill(id):

    if request.method == 'POST':

        current_date = date.today()

        c = HoaDon(phieuThuePhong_id=id, tongTien=request.form.get('total'), ngayLap=current_date)
        db.session.add(c)
        db.session.commit()

        return redirect(url_for('pay'))

    return render_template('hoaDon.html', roomform=dao.get_roomform_by_id(id))


if __name__ == '__main__':
    from app import admin
    app.run(debug=True)