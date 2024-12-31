from app._init_ import app, db
from app.models import *
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose, Admin
from flask_login import logout_user, current_user
from flask import redirect, render_template, request, url_for
import dao


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.loaiNguoiDung == LoaiNguoiDung.ADMIN

    column_display_pk = True
    page_size = 20
    can_export = True
    export_types = ['csv', 'xls']

    column_exclude_list = ['type']
    form_excluded_columns = ['type']


class AdminBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.loaiNguoiDung == LoaiNguoiDung.ADMIN


class UserBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class IndexView(UserBaseView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

class ThongKeView(AdminBaseView):
    @expose('/')
    def index(self):
        revenue_data = dao.get_revenue_data()
        room_type_data = dao.get_room_type_data()
        top_rooms_data = dao.get_top_rooms_data()

        return self.render('admin/stats.html', revenue_data=revenue_data,
                           room_type_data=room_type_data, top_rooms_data=top_rooms_data)


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

admin = Admin(app=app, name='QUẢN TRỊ KHÁCH SẠN', template_mode='bootstrap4')

admin.add_view(AdminModelView(NguoiDung, db.session, name='Người dùng'))
admin.add_view(AdminModelView(LoaiPhong, db.session, name='Loại phòng'))
admin.add_view(AdminModelView(Phong, db.session, name='Phòng'))
admin.add_view(AdminModelView(QuyDinh, db.session, name='Quy định'))
admin.add_view(ThongKeView(name="Thống kê Báo cáo", endpoint='thongke'))
admin.add_view(LogoutView(name="Đăng xuất"))