from rest_framework import permissions


class OrderUpdatePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        elif request.data.get('state', False):
            self.message = 'Менять статус заказа может только администратор'
            return False
        else:
            self.message = 'Клиент может изменять только корзину'
            return obj.state in ["basket"]