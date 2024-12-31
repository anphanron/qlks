from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, Date, Table
from sqlalchemy.orm import relationship
from app._init_ import db
from flask_login import UserMixin
import enum
import hashlib

class LoaiNguoiDung(enum.Enum):
    ADMIN = 1
    NHANVIEN = 2
    KHACHHANG = 3

    def __str__(self):
        return self.name


class TinhTrangPhong(enum.Enum):
    TRONG = 1
    DANG_SU_DUNG = 2
    BAO_TRI = 3

    def __str__(self):
        return self.name


class NguoiDung(db.Model, UserMixin):
    __tablename__ = 'nguoidung'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenDangNhap = Column(String(50), nullable=False, unique=True)
    matKhau = Column(String(100), nullable=False)
    avatar = Column(String(200), default='https://s.net.vn/UqTC')
    hoTen = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    diaChi = Column(String(100), nullable=False)
    soDT = Column(String(100), nullable=False)
    loaiNguoiDung = Column(Enum(LoaiNguoiDung), default=LoaiNguoiDung.KHACHHANG)

    type = Column(String(50))
    __mapper_args__ = {
        'polymorphic_identity': 'nguoidung',
        'polymorphic_on': type
    }

    def __str__(self):
        return self.hoTen


class KhachHang(NguoiDung):
    __tablename__ = 'khachhang'
    maKH = Column(Integer, primary_key=True, autoincrement=True)  # Thay đổi ở đây
    cmnd = Column(String(20), nullable=False)
    nguoi_dung_id = Column(Integer, ForeignKey('nguoidung.id')) # Thêm ở đây
    nguoi_dung = relationship("NguoiDung", backref="khachhang", uselist=False) # Thêm ở đây
    datphongs = relationship('DatPhong', backref='khachhang', lazy=True)

    __mapper_args__ = {
        'polymorphic_identity': 'khachhang',
    }

    def __str__(self):
        return self.hoTen


class NhanVien(NguoiDung):
    __tablename__ = 'nhanvien'
    maNV = Column(Integer, primary_key=True, autoincrement=True)  # Thay đổi ở đây
    nguoi_dung_id = Column(Integer, ForeignKey('nguoidung.id'))  # Thêm ở đây
    nguoi_dung = relationship("NguoiDung", backref="nhanvien", uselist=False)  # Thêm ở đây

    __mapper_args__ = {
        'polymorphic_identity': 'nhanvien',
    }

    def __str__(self):
        return self.hoTen


class NhanVienQuanTri(NguoiDung):
    __tablename__ = 'nhanvienquantri'
    maNVQT = Column(Integer, primary_key=True, autoincrement=True)  # Thay đổi ở đây
    nguoi_dung_id = Column(Integer, ForeignKey('nguoidung.id'))  # Thêm ở đây
    nguoi_dung = relationship("NguoiDung", backref="nhanvienquantri", uselist=False)  # Thêm ở đây
    thongkes = relationship('ThongKe', backref='nhanvienquantri', lazy=True)

    __mapper_args__ = {
        'polymorphic_identity': 'nhanvienquantri',
    }

    def __str__(self):
        return self.hoTen


class LoaiPhong(db.Model):
    __tablename__ = 'loaiphong'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenLoaiPhong = Column(String(100), nullable=False, unique=True)
    phongs = relationship('Phong', backref='loaiphong', lazy=True)
    donGia = Column(Float, default=0)

    def __str__(self):
        return self.tenLoaiPhong


class Phong(db.Model):
    __tablename__ = 'phong'
    maPhong = Column(Integer, primary_key=True, autoincrement=True)
    soPhong = Column(String(100), nullable=False, unique=True)
    moTa = Column(String(200), nullable=False)
    hinhAnh = Column(String(200), nullable=False)
    donGia = Column(Float, default=0)
    tinhTrang = Column(Enum(TinhTrangPhong), default=TinhTrangPhong.TRONG)
    loaiPhong = Column(Integer, ForeignKey(LoaiPhong.id), nullable=False)

    def __str__(self):
        return self.soPhong


chiTietDatPhong_table = Table('chitietdatphong', db.metadata,
                              Column('datPhong_id', Integer, ForeignKey('datphong.maDatPhong'), primary_key=True),
                              Column('phong_id', Integer, ForeignKey('phong.maPhong'), primary_key=True)
                              )


class DatPhong(db.Model):
    __tablename__ = 'datphong'
    maDatPhong = Column(Integer, primary_key=True, autoincrement=True)
    khachHang_id = Column(Integer, ForeignKey(KhachHang.maKH), nullable=False)
    ngayNhan = Column(Date, nullable=False)
    ngayTra = Column(Date, nullable=False)
    phongs = relationship('Phong', secondary=chiTietDatPhong_table, backref='datphongs')
    phieuThuePhong = relationship('PhieuThuePhong', backref='datphong', uselist=False, lazy=True)

    def __str__(self):
        return str(self.maDatPhong)


chiTietPhieuThue_table = Table('chitietphieuthue', db.metadata,
                               Column('phieuThuePhong_id', Integer, ForeignKey('phieuthuephong.maPTP'),
                                      primary_key=True),
                               Column('khachHang_id', Integer, ForeignKey('khachhang.maKH'), primary_key=True)
                               )


class PhieuThuePhong(db.Model):
    __tablename__ = 'phieuthuephong'
    maPTP = Column(Integer, primary_key=True, autoincrement=True)
    datPhong_id = Column(Integer, ForeignKey(DatPhong.maDatPhong), nullable=False)
    dsKhach = relationship('KhachHang', secondary=chiTietPhieuThue_table, backref='phieuthuephongs')
    ngayNhan = Column(Date, nullable=False)
    ngayTra = Column(Date, nullable=False)
    soNguoi = Column(Integer, default=1)
    hoaDon = relationship('HoaDon', backref='thuephong', uselist=False, lazy=True)

    def __str__(self):
        return str(self.maPTP)


class HoaDon(db.Model):
    __tablename__ = 'hoadon'
    maHD = Column(Integer, primary_key=True, autoincrement=True)
    phieuThuePhong_id = Column(Integer, ForeignKey(PhieuThuePhong.maPTP), nullable=False)
    tongTien = Column(Float, nullable=True)
    ngayLap = Column(Date, nullable=False)

    def __str__(self):
        return str(self.maHD)


class ThongKe(db.Model):
    __tablename__ = 'thongke'
    id = Column(Integer, primary_key=True, autoincrement=True)
    thang = Column(Integer, nullable=False)
    doanhThu = Column(Float, nullable=False)
    tanSuat = Column(Integer, nullable=False)
    nhanVienQuanTri_id = Column(Integer, ForeignKey(NhanVienQuanTri.maNVQT), nullable=False)

    def __str__(self):
        return "Thống kê tháng " + str(self.thang)


class QuyDinh(db.Model):
    __tablename__ = 'quydinh'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenQuyDinh = Column(String(100), nullable=False)
    soKhachToiDa = Column(Integer, nullable=False)
    phuThuKhachThu3 = Column(Float, nullable=False)

    def __str__(self):
        return self.tenQuyDinh

if __name__ == '__main__':
    from app._init_ import app

    with app.app_context():
        db.create_all()

        # Tạo NhanVienQuanTri
        user1 = NguoiDung(tenDangNhap='admin',
                          matKhau=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
                          hoTen='Admin',
                          email='admin@gmail.com',
                          diaChi='HCM',
                          soDT='0849165932',
                          loaiNguoiDung=LoaiNguoiDung.ADMIN,
                          type='nhanvienquantri')
        nvqt1 = NhanVienQuanTri(nguoi_dung_id=user1.id)

        # Tạo NhanVien
        user2 = NguoiDung(tenDangNhap='quyan',
                          matKhau=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
                          hoTen='QuyAn',
                          email='quyan@gmail.com',
                          diaChi='Hoc Mon',
                          soDT='0392995499',
                          loaiNguoiDung=LoaiNguoiDung.NHANVIEN,
                          type='nhanvien')
        nv1 = NhanVien(nguoi_dung_id=user2.id)

        user3 = NguoiDung(tenDangNhap='nguyentuyen',
                          matKhau=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
                          hoTen='NguyenTuyen',
                          email='nguyentuyen@gmail.com',
                          diaChi='Vung Tau',
                          soDT='0775438606',
                          loaiNguoiDung=LoaiNguoiDung.NHANVIEN,
                          type='nhanvien')
        nv2 = NhanVien(nguoi_dung_id=user3.id)

        user4 = NguoiDung(tenDangNhap='thienan',
                          matKhau=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
                          hoTen='ThienAn',
                          email='thienan@gmail.com',
                          diaChi='Go Vap',
                          soDT='0977751951',
                          loaiNguoiDung=LoaiNguoiDung.NHANVIEN,
                          type='nhanvien')
        nv3 = NhanVien(nguoi_dung_id=user4.id)
        db.session.add_all([user1,user2,user3,user4])

        type1 = LoaiPhong(tenLoaiPhong='Phòng President', donGia=5000000)
        type2 = LoaiPhong(tenLoaiPhong='Phòng Premium', donGia=3000000)
        type3 = LoaiPhong(tenLoaiPhong='Phòng Luxury', donGia=2000000)
        type4 = LoaiPhong(tenLoaiPhong='Phòng Studio', donGia=1500000)
        type5 = LoaiPhong(tenLoaiPhong='Phòng Executive', donGia=1000000)
        db.session.add_all([type1, type2, type3, type4, type5])

        db.session.commit()
        room1 = Phong(soPhong='P001',
                      moTa='THE ROOM FOR THE PRESIDENT, THE HEADS OF STATE',
                      hinhAnh='https://rosaalbaresort.com/wp-content/uploads/2023/10/RAS3-2048x1365.jpg',
                      donGia=5000000,
                      loaiPhong=type1.id,
                      tinhTrang=TinhTrangPhong.TRONG)
        room2 = Phong(soPhong='P002',
                      moTa='A DISTINGUISHED YET COMFORTABLE AMBIENCE',
                      hinhAnh='https://rosaalbaresort.com/wp-content/uploads/2023/10/PDT11-scaled.jpg',
                      donGia=3000000,
                      loaiPhong=type2.id,
                      tinhTrang=TinhTrangPhong.TRONG)
        room3 = Phong(soPhong='P003',
                      moTa='INSPIRE ROMANTIC MEMORIES WITH A TRULY CHARMING RETREAT',
                      hinhAnh='https://rosaalbaresort.com/wp-content/uploads/2023/10/SD5-2048x1365.jpg',
                      donGia=2000000,
                      loaiPhong=type3.id,
                      tinhTrang=TinhTrangPhong.TRONG)
        room4 = Phong(soPhong='P004',
                      moTa='INSPIRE ROMANTIC MEMORIES WITH A TRULY CHARMING RETREAT',
                      hinhAnh='https://rosaalbaresort.com/wp-content/uploads/2023/10/ST4-2048x1365.jpg',
                      donGia=1500000,
                      loaiPhong=type4.id,
                      tinhTrang=TinhTrangPhong.TRONG)
        room5 = Phong(soPhong='P005',
                      moTa='THE TASTEFULLY DECORATED OFFER A HIGH LEVEL OF LUXURY',
                      hinhAnh='https://rosaalbaresort.com/wp-content/uploads/2023/10/ES3-2048x1365.jpg',
                      donGia=1000000,
                      loaiPhong=type5.id,
                      tinhTrang=TinhTrangPhong.TRONG)
        db.session.add_all([room1, room2, room3, room4, room5])
        db.session.commit()
