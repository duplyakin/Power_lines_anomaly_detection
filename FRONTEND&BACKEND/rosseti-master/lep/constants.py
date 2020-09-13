from django.utils.translation import gettext_lazy as _


GENDER_CHOICES = (
    (0, _('Male')),
    (1, _('Female')),
    (2, _('Other')),
)

EMAIL_NOTIFY_CHOICES = (
    (0, _('Disable')),
    (1, _('Enable')),
)

ROOM_TYPE_CHOICES = (
    (0, _('Public')),
    (1, _('Private')),
    (2, _('Hidden')),
)

MESSAGE_STATUS_CHOICES = (
    (0, _('Deleted')),
    (1, _('Active')),
    (2, _('Hidden')),
)

INVITE_REASON_CHOICES = (
    (0, _('Create room')),
    (1, _('Buy ticket')),
    (2, _('Owner add')),
    (3, _('Free access')),
)

# NAVBAR names
NAVBAR_MAIN = 'navbar_main'
NAVBAR_PROFILE = 'navbar_profile'
NAVBAR_EVENT = 'navbar_event'
NAVBAR_ROOM_LIST = 'navbar_room_list'
NAVBAR_USER_ACCOUNT = 'navbar_user_account'
NAVBAR_INDEX_ANALYSE = 'navbar_index_analyse'
NAVBAR_IMAGE_UPLOAD = 'navbar_image_upload'
NAVBAR_INDEX_DASHBOARD = 'navbar_index_dashboard'

# Status for LEP accident
STATUS_PROBABLY = 'Возможно'
STATUS_ANALYSE = 'Анализируем'
STATUS_NOT_DETECTED = 'Необнаружено'
