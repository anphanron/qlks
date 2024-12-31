import hashlib
from app.models import Phong, LoaiPhong, NguoiDung, HoaDon, PhieuThuePhong, DatPhong, chiTietDatPhong_table
from app._init_ import app, db
from sqlalchemy import func, extract
from datetime import datetime

def load_rooms(kw=None, type_id=None, pricefrom=None, priceto=None, page=1):
    rooms = Phong.query

    if kw:
        rooms = rooms.filter(Phong.soPhong.contains(kw))

    if type_id:
        rooms = rooms.filter(Phong.loaiPhong == type_id)
    if pricefrom:
        rooms = rooms.filter(Phong.donGia >= pricefrom)

    if priceto:
        rooms = rooms.filter(Phong.donGia <= priceto)
    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    end = start + page_size
    return rooms.slice(start, end).all()


def count_room():
    return Phong.query.count()


def get_room_by_id(room_id):
    return Phong.query.get(room_id)


def load_roomform():
    return LoaiPhong.query.all()


def load_typeroom():
    return LoaiPhong.query.all()


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return NguoiDung.query.filter(NguoiDung.tenDangNhap.__eq__(username.strip()),
                                  NguoiDung.matKhau.__eq__(password)).first()


def get_user_by_id(user_id):
    return NguoiDung.query.get(user_id)


def get_roomform_by_id(id):
    return LoaiPhong.query.get(id)

def get_revenue_data(year=None):
    if year is None:
        year = datetime.now().year
    query = db.session.query(
        extract('month', HoaDon.ngayLap),
        func.sum(HoaDon.tongTien)
    ).filter(extract('year', HoaDon.ngayLap) == year) \
        .group_by(extract('month', HoaDon.ngayLap)) \
        .order_by(extract('month', HoaDon.ngayLap))

    result = query.all()

    labels = []
    data = []
    for month, total in result:
        labels.append(f'Tháng {month}')
        data.append(float(total))

    return {
        'labels': labels,
        'data': data
    }


def get_room_type_data():
    query = db.session.query(
        LoaiPhong.tenLoaiPhong,
        func.count(DatPhong.maDatPhong)
    ).outerjoin(Phong, LoaiPhong.id == Phong.loaiPhong) \
        .outerjoin(chiTietDatPhong_table, Phong.maPhong == chiTietDatPhong_table.c.phong_id) \
        .outerjoin(DatPhong, chiTietDatPhong_table.c.datPhong_id == DatPhong.maDatPhong) \
        .group_by(LoaiPhong.tenLoaiPhong)

    result = query.all()

    # Chuẩn hóa dữ liệu
    labels = [row[0] for row in result]
    data = [row[1] for row in result]

    return {
        'labels': labels,
        'data': data
    }


def get_top_rooms_data():
    result = db.session.query(Phong.soPhong, LoaiPhong.tenLoaiPhong, func.sum(HoaDon.tongTien)) \
        .join(LoaiPhong, Phong.loaiPhong == LoaiPhong.id) \
        .join(chiTietDatPhong_table, Phong.maPhong == chiTietDatPhong_table.c.phong_id) \
        .join(DatPhong, chiTietDatPhong_table.c.datPhong_id == DatPhong.maDatPhong) \
        .join(PhieuThuePhong, DatPhong.maDatPhong == PhieuThuePhong.datPhong_id) \
        .join(HoaDon, PhieuThuePhong.maPTP == HoaDon.phieuThuePhong_id) \
        .group_by(Phong.soPhong, LoaiPhong.tenLoaiPhong) \
        .order_by(func.sum(HoaDon.tongTien).desc()) \
        .limit(5) \
        .all()

    return [
        {
            'soPhong': row[0],
            'loaiPhong': row[1],
            'doanhThu': float(row[2])
        }
        for row in result
    ]


def get_available_rooms(typeroom, ngayNhan):
    """
    Lấy danh sách các phòng trống dựa trên loại phòng và ngày nhận.
    """
    print(f"typeroom: {typeroom}")
    print(f"ngayNhan: {ngayNhan}")

    # Chuyển đổi ngayNhan từ string sang date object
    ngayNhan_date = datetime.strptime(ngayNhan, '%Y-%m-%d').date()

    # Lấy danh sách các phòng thuộc loại phòng đã chọn
    rooms_of_type = Phong.query.join(LoaiPhong).filter(LoaiPhong.tenLoaiPhong == typeroom).all()
    print(f"rooms_of_type: {rooms_of_type}")

    available_rooms = []
    for room in rooms_of_type:
        # Kiểm tra xem phòng có được đặt trong ngày đã cho hay không
        is_booked = any(
            booking.ngayNhan <= ngayNhan_date <= booking.ngayTra
            for booking in room.datphongs
        )
        print(f"room: {room.soPhong}, is_booked: {is_booked}")
        # Nếu phòng không được đặt, thêm nó vào danh sách phòng trống
        if not is_booked:
            available_rooms.append(room)

    print(f"available_rooms: {available_rooms}")
    return available_rooms