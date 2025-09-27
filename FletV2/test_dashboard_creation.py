#!/usr/bin/env python3
"""
Test script to check if dashboard creation works without Flet app.
"""

import os
import sys
import types  # Added import for types.ModuleType

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
repo_root = os.path.dirname(parent_dir)

for path in (parent_dir, repo_root):
    if path not in sys.path:
        sys.path.insert(0, path)

# Mock Flet to avoid GUI dependencies
class MockControl:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def update(self):
        pass

# Mock other modules (moved MockPsutil here to ensure it's defined before use)
class MockPsutil:
    def cpu_percent(self, interval=None):
        return 50.0
    def virtual_memory(self):
        class Memory:
            percent = 60.0
        return Memory()
    def disk_usage(self, path):
        class Disk:
            percent = 70.0
        return Disk()

class MockFlet:
    def __init__(self):
        self.Controls = self
        self.Text = MockControl
        self.Column = MockControl
        self.Container = MockControl
        self.Row = MockControl
        self.Card = MockControl
        self.ProgressRing = MockControl
        self.ElevatedButton = MockControl
        self.FilledButton = MockControl
        self.FilledTonalButton = MockControl
        self.OutlinedButton = MockControl
        self.Icon = MockControl
        self.ProgressBar = MockControl
        self.DataTable = MockControl
        self.DataColumn = MockControl
        self.DataRow = MockControl
        self.DataCell = MockControl
        self.ListView = MockControl
        self.PieChart = MockControl
        self.PieChartSection = MockControl
        self.BarChart = MockControl
        self.BarChartRodData = MockControl
        self.BarChartGroup = MockControl
        self.BarChartRodStackItem = MockControl
        self.BarChartEvent = MockControl
        self.BarChartEventType = MockControl
        self.LineChart = MockControl
        self.LineChartData = MockControl
        self.LineChartDataPoint = MockControl
        self.FilterChip = MockControl
        self.Chip = MockControl
        self.Shimmer = MockControl
        self.AnimatedSwitcher = MockControl
        self.VerticalDivider = MockControl
        self.NavigationRail = MockControl
        self.NavigationRailDestination = MockControl
        self.PopupMenuButton = MockControl
        self.PopupMenuItem = MockControl
        self.TextButton = MockControl
        self.Dropdown = MockControl
        self.TextField = MockControl
        self.Checkbox = MockControl
        self.Switch = MockControl
        self.Slider = MockControl
        self.RadioGroup = MockControl
        self.Radio = MockControl
        self.DatePicker = MockControl
        self.TimePicker = MockControl
        self.FilePicker = MockControl
        self.Image = MockControl
        self.CircleAvatar = MockControl
        self.Badge = MockControl
        self.Divider = MockControl
        self.ExpansionPanel = MockControl
        self.ExpansionPanelList = MockControl
        self.Tabs = MockControl
        self.Tab = MockControl
        self.GridView = MockControl
        self.ResponsiveRow = MockControl
        self.Column = MockControl
        self.Row = MockControl
        self.Stack = MockControl
        self.AlertDialog = MockControl
        self.SnackBar = MockControl
        self.Banner = MockControl
        self.BottomSheet = MockControl
        self.Drawer = MockControl
        self.AppBar = MockControl
        self.BottomAppBar = MockControl
        self.FloatingActionButton = MockControl
        self.SpeedDial = MockControl
        self.SpeedDialChild = MockControl

        # Colors
        self.Colors = self
        self.PRIMARY = "#1976D2"
        self.ON_PRIMARY = "#FFFFFF"
        self.SECONDARY = "#DC3545"
        self.ON_SECONDARY = "#FFFFFF"
        self.SURFACE = "#FFFFFF"
        self.ON_SURFACE = "#000000"
        self.BACKGROUND = "#FAFAFA"
        self.ERROR = "#F44336"
        self.ON_ERROR = "#FFFFFF"
        self.OUTLINE = "#BDBDBD"
        self.SURFACE_VARIANT = "#EEEEEE"
        self.ON_SURFACE_VARIANT = "#000000"
        self.SURFACE_TINT = "#1976D2"
        self.BLUE = "#2196F3"
        self.GREEN = "#4CAF50"
        self.RED = "#F44336"
        self.ORANGE = "#FF9800"
        self.PURPLE = "#9C27B0"
        self.PINK = "#E91E63"
        self.CYAN = "#00BCD4"
        self.AMBER = "#FFC107"
        self.INDIGO = "#3F51B5"
        self.LIME = "#CDDC39"
        self.TEAL = "#009688"
        self.BROWN = "#795548"
        self.GREY = "#9E9E9E"
        self.BLUE_GREY = "#607D8B"

        # Icons
        self.Icons = self
        self.DASHBOARD = "dashboard"
        self.DASHBOARD_OUTLINED = "dashboard_outlined"
        self.PEOPLE = "people"
        self.PEOPLE_OUTLINE = "people_outline"
        self.FOLDER = "folder"
        self.FOLDER_OPEN = "folder_open"
        self.STORAGE = "storage"
        self.STORAGE_OUTLINED = "storage_outlined"
        self.AUTO_GRAPH = "auto_graph"
        self.AUTO_GRAPH_OUTLINED = "auto_graph_outlined"
        self.ARTICLE = "article"
        self.ARTICLE_OUTLINED = "article_outlined"
        self.SETTINGS = "settings"
        self.REFRESH = "refresh"
        self.PLAY_ARROW = "play_arrow"
        self.STOP = "stop"
        self.BACKUP = "backup"
        self.SYNC = "sync"
        self.ERROR = "error"
        self.ERROR_OUTLINED = "error_outlined"
        self.WARNING = "warning"
        self.INFO = "info"
        self.CHECK_CIRCLE = "check_circle"
        self.CANCEL = "cancel"
        self.EDIT = "edit"
        self.DELETE = "delete"
        self.ADD = "add"
        self.REMOVE = "remove"
        self.SEARCH = "search"
        self.FILTER_LIST = "filter_list"
        self.SORT = "sort"
        self.MORE_VERT = "more_vert"
        self.MORE_HORIZ = "more_horiz"
        self.EXPAND_MORE = "expand_more"
        self.EXPAND_LESS = "expand_less"
        self.KEYBOARD_ARROW_UP = "keyboard_arrow_up"
        self.KEYBOARD_ARROW_DOWN = "keyboard_arrow_down"
        self.KEYBOARD_ARROW_LEFT = "keyboard_arrow_left"
        self.KEYBOARD_ARROW_RIGHT = "keyboard_arrow_right"
        self.ARROW_UPWARD = "arrow_upward"
        self.ARROW_DOWNWARD = "arrow_downward"
        self.ARROW_BACK = "arrow_back"
        self.ARROW_FORWARD = "arrow_forward"
        self.CHEVRON_LEFT = "chevron_left"
        self.CHEVRON_RIGHT = "chevron_right"
        self.TRENDING_UP = "trending_up"
        self.TRENDING_DOWN = "trending_down"
        self.TRENDING_FLAT = "trending_flat"
        self.UPDATE = "update"
        self.ACCESS_TIME = "access_time"
        self.CALENDAR_TODAY = "calendar_today"
        self.EVENT = "event"
        self.SCHEDULE = "schedule"
        self.TIMER = "timer"
        self.HOURGLASS_EMPTY = "hourglass_empty"
        self.HOURGLASS_FULL = "hourglass_full"
        self.SECURITY = "security"
        self.LOCK = "lock"
        self.LOCK_OPEN = "lock_open"
        self.VISIBILITY = "visibility"
        self.VISIBILITY_OFF = "visibility_off"
        self.KEY = "key"
        self.VPN_KEY = "vpn_key"
        self.SHIELD = "shield"
        self.SECURITY_UPDATE = "security_update"
        self.BUG_REPORT = "bug_report"
        self.HELP = "help"
        self.HELP_OUTLINE = "help_outline"
        self.SUPPORT = "support"
        self.FEEDBACK = "feedback"
        self.ANNOUNCEMENT = "announcement"
        self.CAMPAIGN = "campaign"
        self.CAMPAIGN_OUTLINED = "campaign_outlined"
        self.NOTIFICATIONS = "notifications"
        self.NOTIFICATIONS_ACTIVE = "notifications_active"
        self.NOTIFICATIONS_NONE = "notifications_none"
        self.NOTIFICATIONS_OFF = "notifications_off"
        self.NOTIFICATIONS_PAUSED = "notifications_paused"
        self.MAIL = "mail"
        self.MAIL_OUTLINE = "mail_outline"
        self.INBOX = "inbox"
        self.OUTBOX = "outbox"
        self.SEND = "send"
        self.DRAFTS = "drafts"
        self.ARCHIVE = "archive"
        self.UNARCHIVE = "unarchive"
        self.DELETE_SWEEP = "delete_sweep"
        self.RESTORE_FROM_TRASH = "restore_from_trash"
        self.SNOOZE = "snooze"
        self.STAR = "star"
        self.STAR_OUTLINE = "star_outline"
        self.STAR_HALF = "star_half"
        self.FLAG = "flag"
        self.FLAG_OUTLINE = "flag_outline"
        self.BOOKMARK = "bookmark"
        self.BOOKMARK_OUTLINE = "bookmark_outline"
        self.LABEL = "label"
        self.LABEL_OUTLINE = "label_outline"
        self.TAG = "tag"
        self.LABELS = "labels"
        self.FOLDER_SPECIAL = "folder_special"
        self.DRIVE_FILE_MOVE = "drive_file_move"
        self.FILE_DOWNLOAD = "file_download"
        self.FILE_UPLOAD = "file_upload"
        self.CLOUD = "cloud"
        self.CLOUD_DONE = "cloud_done"
        self.CLOUD_DOWNLOAD = "cloud_download"
        self.CLOUD_UPLOAD = "cloud_upload"
        self.CLOUD_OFF = "cloud_off"
        self.CLOUD_QUEUE = "cloud_queue"
        self.CREATE_NEW_FOLDER = "create_new_folder"
        self.FOLDER_SHARED = "folder_shared"
        self.SNIPPET_FOLDER = "snippet_folder"
        self.RULE_FOLDER = "rule_folder"
        self.TOPIC = "topic"
        self.SNIPPET_FOLDER_OUTLINED = "snippet_folder_outlined"
        self.RULE_FOLDER_OUTLINED = "rule_folder_outlined"
        self.TOPIC_OUTLINED = "topic_outlined"
        self.ATTACHMENT = "attachment"
        self.ATTACH_FILE = "attach_file"
        self.ATTACH_MONEY = "attach_money"
        self.LINK = "link"
        self.LINK_OFF = "link_off"
        self.LOW_PRIORITY = "low_priority"
        self.HIGH_PRIORITY = "high_priority"
        self.BLOCK = "block"
        self.UNBLOCK = "unblock"
        self.UNDO = "undo"
        self.REDO = "redo"
        self.CONTENT_COPY = "content_copy"
        self.CONTENT_CUT = "content_cut"
        self.CONTENT_PASTE = "content_paste"
        self.SELECT_ALL = "select_all"
        self.CLEAR = "clear"
        self.REMOVE_CIRCLE = "remove_circle"
        self.REMOVE_CIRCLE_OUTLINE = "remove_circle_outline"
        self.ADD_CIRCLE = "add_circle"
        self.ADD_CIRCLE_OUTLINE = "add_circle_outline"
        self.CANCEL_PRESENTATION = "cancel_presentation"
        self.PAUSE_PRESENTATION = "pause_presentation"
        self.STOP_SCREEN_SHARE = "stop_screen_share"
        self.CALL_TO_ACTION = "call_to_action"
        self.BUSINESS = "business"
        self.BUSINESS_CENTER = "business_center"
        self.LOCATION_ON = "location_on"
        self.LOCATION_OFF = "location_off"
        self.MAP = "map"
        self.MY_LOCATION = "my_location"
        self.NAVIGATION = "navigation"
        self.NEAR_ME = "near_me"
        self.PERSON = "person"
        self.PERSON_ADD = "person_add"
        self.PERSON_OUTLINE = "person_outline"
        self.PERSON_ADD_ALT = "person_add_alt"
        self.PERSON_REMOVE = "person_remove"
        self.CONTACTS = "contacts"
        self.CONTACT_MAIL = "contact_mail"
        self.CONTACT_PHONE = "contact_phone"
        self.RECENT_ACTORS = "recent_actors"
        self.GROUP = "group"
        self.GROUP_ADD = "group_add"
        self.GROUP_WORK = "group_work"
        self.SCHOOL = "school"
        self.DOMAIN = "domain"
        self.DOMAIN_DISABLED = "domain_disabled"
        self.WORK = "work"
        self.ENGINEERING = "engineering"
        self.CONSTRUCTION = "construction"
        self.ACCOUNT_CIRCLE = "account_circle"
        self.SWITCH_ACCOUNT = "switch_account"
        self.MANAGE_ACCOUNTS = "manage_accounts"
        self.VERIFIED_USER = "verified_user"
        self.GAVEL = "gavel"
        self.PAN_TOOL = "pan_tool"
        self.CONTENT_SAVE = "content_save"
        self.CONTENT_SAVE_ALT = "content_save_alt"
        self.CONTENT_SAVE_OUTLINED = "content_save_outlined"
        self.DELETE_FOREVER = "delete_forever"
        self.RESTORE = "restore"
        self.BACKUP_TABLE = "backup_table"
        self.CLOUD_SYNC = "cloud_sync"
        self.DRIVE_FOLDER_UPLOAD = "drive_folder_upload"
        self.CREATE = "create"
        self.CREATE_NEW_FOLDER_OUTLINED = "create_new_folder_outlined"
        self.FOLDER_COPY = "folder_copy"
        self.FOLDER_DELETE = "folder_delete"
        self.FOLDER_MOVE = "folder_move"
        self.FOLDER_OPEN_OUTLINED = "folder_open_outlined"
        self.FOLDER_SHARED_OUTLINED = "folder_shared_outlined"
        self.FOLDER_SPECIAL_OUTLINED = "folder_special_outlined"
        self.DRIVE_FILE_MOVE_OUTLINED = "drive_file_move_outlined"
        self.FILE_DOWNLOAD_DONE = "file_download_done"
        self.FILE_PRESENT = "file_present"
        self.FILE_UPLOAD_OUTLINED = "file_upload_outlined"
        self.CLOUD_DONE_OUTLINED = "cloud_done_outlined"
        self.CLOUD_DOWNLOAD_OUTLINED = "cloud_download_outlined"
        self.CLOUD_UPLOAD_OUTLINED = "cloud_upload_outlined"
        self.CLOUD_OFF_OUTLINED = "cloud_off_outlined"
        self.CLOUD_QUEUE_OUTLINED = "cloud_queue_outlined"
        self.TEXT_SNIPPET = "text_snippet"
        self.TEXT_SNIPPET_OUTLINED = "text_snippet_outlined"
        self.NOTE = "note"
        self.NOTE_ADD = "note_add"
        self.NOTE_ALT = "note_alt"
        self.STICKY_NOTE_2 = "sticky_note_2"
        self.STICKY_NOTE_2_OUTLINED = "sticky_note_2_outlined"
        self.DESCRIPTION = "description"
        self.FEED = "feed"
        self.ARTICLE_OUTLINED = "article_outlined"
        self.NEWSPAPER = "newspaper"
        self.EVENT_NOTE = "event_note"
        self.EVENT_AVAILABLE = "event_available"
        self.EVENT_BUSY = "event_busy"
        self.CALENDAR_VIEW_DAY = "calendar_view_day"
        self.CALENDAR_VIEW_WEEK = "calendar_view_week"
        self.CALENDAR_VIEW_MONTH = "calendar_view_month"
        self.SCHEDULE_SEND = "schedule_send"
        self.PENDING_ACTIONS = "pending_actions"
        self.FREE_CANCELLATION = "free_cancellation"
        self.EVENT_SEAT = "event_seat"
        self.FLIGHT_LAND = "flight_land"
        self.FLIGHT_TAKEOFF = "flight_takeoff"
        self.AIRPLANEMODE_ACTIVE = "airplanemode_active"
        self.AIRPLANEMODE_INACTIVE = "airplanemode_inactive"
        self.DIRECTIONS_CAR = "directions_car"
        self.DIRECTIONS_BUS = "directions_bus"
        self.DIRECTIONS_BIKE = "directions_bike"
        self.DIRECTIONS_BOAT = "directions_boat"
        self.DIRECTIONS_SUBWAY = "directions_subway"
        self.DIRECTIONS_RAILWAY = "directions_railway"
        self.DIRECTIONS_TRANSIT = "directions_transit"
        self.DIRECTIONS_WALK = "directions_walk"
        self.TRAIN = "train"
        self.TRAM = "tram"
        self.BUS_ALERT = "bus_alert"
        self.DEPARTURE_BOARD = "departure_board"
        self.TRANSIT_ENTEREXIT = "transit_enterexit"
        self.COMMUTE = "commute"
        self.ELECTRIC_BIKE = "electric_bike"
        self.ELECTRIC_CAR = "electric_car"
        self.ELECTRIC_MOPED = "electric_moped"
        self.ELECTRIC_SCOOTER = "electric_scooter"
        self.PEDAL_BIKE = "pedal_bike"
        self.TWO_WHEELER = "two_wheeler"
        self.NO_CRASH = "no_crash"
        self.BIKE_SCOOTER = "bike_scooter"
        self.ELECTRIC_RICKSHAW = "electric_rickshaw"
        self.MOTORCYCLE = "motorcycle"
        self.CAR_RENTAL = "car_rental"
        self.CAR_REPAIR = "car_repair"
        self.EV_STATION = "ev_station"
        self.GAS_STATION = "gas_station"
        self.CHARGING_STATION = "charging_station"
        self.LOCAL_SHIPPING = "local_shipping"
        self.LOCAL_AIRPORT = "local_airport"
        self.AIRLINE_SEAT_FLAT = "airline_seat_flat"
        self.AIRLINE_SEAT_FLAT_ANGLED = "airline_seat_flat_angled"
        self.AIRLINE_SEAT_INDIVIDUAL_SUITE = "airline_seat_individual_suite"
        self.AIRLINE_SEAT_LEGROOM_EXTRA = "airline_seat_legroom_extra"
        self.AIRLINE_SEAT_LEGROOM_NORMAL = "airline_seat_legroom_normal"
        self.AIRLINE_SEAT_LEGROOM_REDUCED = "airline_seat_legroom_reduced"
        self.AIRLINE_SEAT_RECLINE_EXTRA = "airline_seat_reclined_extra"
        self.AIRLINE_SEAT_RECLINE_NORMAL = "airline_seat_recline_normal"
        self.ELECTRIC_RICKSHAW_OUTLINED = "electric_rickshaw_outlined"
        self.MOTORCYCLE_OUTLINED = "motorcycle_outlined"
        self.CAR_RENTAL_OUTLINED = "car_rental_outlined"
        self.CAR_REPAIR_OUTLINED = "car_repair_outlined"
        self.EV_STATION_OUTLINED = "ev_station_outlined"
        self.GAS_STATION_OUTLINED = "gas_station_outlined"
        self.CHARGING_STATION_OUTLINED = "charging_station_outlined"
        self.LOCAL_SHIPPING_OUTLINED = "local_shipping_outlined"
        self.LOCAL_AIRPORT_OUTLINED = "local_airport_outlined"
        self.AIRLINE_SEAT_FLAT_OUTLINED = "airline_seat_flat_outlined"
        self.AIRLINE_SEAT_FLAT_ANGLED_OUTLINED = "airline_seat_flat_angled_outlined"
        self.AIRLINE_SEAT_INDIVIDUAL_SUITE_OUTLINED = "airline_seat_individual_suite_outlined"
        self.AIRLINE_SEAT_LEGROOM_EXTRA_OUTLINED = "airline_seat_legroom_extra_outlined"
        self.AIRLINE_SEAT_LEGROOM_NORMAL_OUTLINED = "airline_seat_legroom_normal_outlined"
        self.AIRLINE_SEAT_LEGROOM_REDUCED_OUTLINED = "airline_seat_legroom_reduced_outlined"
        self.AIRLINE_SEAT_RECLINE_EXTRA_OUTLINED = "airline_seat_recline_extra_outlined"
        self.AIRLINE_SEAT_RECLINE_NORMAL_OUTLINED = "airline_seat_recline_normal_outlined"
        self.ELECTRIC_BIKE_OUTLINED = "electric_bike_outlined"
        self.ELECTRIC_CAR_OUTLINED = "electric_car_outlined"
        self.ELECTRIC_MOPED_OUTLINED = "electric_moped_outlined"
        self.ELECTRIC_SCOOTER_OUTLINED = "electric_scooter_outlined"
        self.PEDAL_BIKE_OUTLINED = "pedal_bike_outlined"
        self.TWO_WHEELER_OUTLINED = "two_wheeler_outlined"
        self.NO_CRASH_OUTLINED = "no_crash_outlined"
        self.BIKE_SCOOTER_OUTLINED = "bike_scooter_outlined"
        self.DIRECTIONS_CAR_OUTLINED = "directions_car_outlined"
        self.DIRECTIONS_BUS_OUTLINED = "directions_bus_outlined"
        self.DIRECTIONS_BIKE_OUTLINED = "directions_bike_outlined"
        self.DIRECTIONS_BOAT_OUTLINED = "directions_boat_outlined"
        self.DIRECTIONS_SUBWAY_OUTLINED = "directions_subway_outlined"
        self.DIRECTIONS_RAILWAY_OUTLINED = "directions_railway_outlined"
        self.DIRECTIONS_TRANSIT_OUTLINED = "directions_transit_outlined"
        self.DIRECTIONS_WALK_OUTLINED = "directions_walk_outlined"
        self.TRAIN_OUTLINED = "train_outlined"
        self.TRAM_OUTLINED = "tram_outlined"
        self.BUS_ALERT_OUTLINED = "bus_alert_outlined"
        self.DEPARTURE_BOARD_OUTLINED = "departure_board_outlined"
        self.TRANSIT_ENTEREXIT_OUTLINED = "transit_enterexit_outlined"
        self.COMMUTE_OUTLINED = "commute_outlined"
        self.FLIGHT_LAND_OUTLINED = "flight_land_outlined"
        self.FLIGHT_TAKEOFF_OUTLINED = "flight_takeoff_outlined"
        self.AIRPLANEMODE_ACTIVE_OUTLINED = "airplanemode_active_outlined"
        self.AIRPLANEMODE_INACTIVE_OUTLINED = "airplanemode_inactive_outlined"
        self.PERSON_OUTLINE = "person_outline"
        self.PERSON_ADD_OUTLINED = "person_add_outlined"
        self.PERSON_ADD_ALT_OUTLINED = "person_add_alt_outlined"
        self.PERSON_REMOVE_OUTLINED = "person_remove_outlined"
        self.CONTACTS_OUTLINED = "contacts_outlined"
        self.CONTACT_MAIL_OUTLINED = "contact_mail_outlined"
        self.CONTACT_PHONE_OUTLINED = "contact_phone_outlined"
        self.RECENT_ACTORS_OUTLINED = "recent_actors_outlined"
        self.GROUP_OUTLINED = "group_outlined"
        self.GROUP_ADD_OUTLINED = "group_add_outlined"
        self.GROUP_WORK_OUTLINED = "group_work_outlined"
        self.SCHOOL_OUTLINED = "school_outlined"
        self.DOMAIN_OUTLINED = "domain_outlined"
        self.DOMAIN_DISABLED_OUTLINED = "domain_disabled_outlined"
        self.WORK_OUTLINED = "work_outlined"
        self.ENGINEERING_OUTLINED = "engineering_outlined"
        self.CONSTRUCTION_OUTLINED = "construction_outlined"
        self.ACCOUNT_CIRCLE_OUTLINED = "account_circle_outlined"
        self.SWITCH_ACCOUNT_OUTLINED = "switch_account_outlined"
        self.MANAGE_ACCOUNTS_OUTLINED = "manage_accounts_outlined"
        self.VERIFIED_USER_OUTLINED = "verified_user_outlined"
        self.GAVEL_OUTLINED = "gavel_outlined"
        self.PAN_TOOL_OUTLINED = "pan_tool_outlined"
        self.CONTENT_SAVE_OUTLINED = "content_save_outlined"
        self.CONTENT_SAVE_ALT_OUTLINED = "content_save_outlined"
        self.DELETE_FOREVER_OUTLINED = "delete_forever_outlined"
        self.RESTORE_OUTLINED = "restore_outlined"
        self.BACKUP_TABLE_OUTLINED = "backup_table_outlined"
        self.CLOUD_SYNC_OUTLINED = "cloud_sync_outlined"
        self.DRIVE_FOLDER_UPLOAD_OUTLINED = "drive_folder_upload_outlined"
        self.CREATE_OUTLINED = "create_outlined"
        self.FOLDER_COPY_OUTLINED = "folder_copy_outlined"
        self.FOLDER_DELETE_OUTLINED = "folder_delete_outlined"
        self.FOLDER_MOVE_OUTLINED = "folder_move_outlined"
        self.FILE_DOWNLOAD_OUTLINED = "file_download_outlined"
        self.FILE_PRESENT_OUTLINED = "file_present_outlined"
        self.TEXT_SNIPPET_OUTLINED = "text_snippet_outlined"
        self.NOTE_OUTLINED = "note_outlined"
        self.NOTE_ADD_OUTLINED = "note_add_outlined"
        self.NOTE_ALT_OUTLINED = "note_alt_outlined"
        self.STICKY_NOTE_2_OUTLINED = "sticky_note_2_outlined"
        self.DESCRIPTION_OUTLINED = "description_outlined"
        self.FEED_OUTLINED = "feed_outlined"
        self.NEWSPAPER_OUTLINED = "newspaper_outlined"
        self.EVENT_NOTE_OUTLINED = "event_note_outlined"
        self.EVENT_AVAILABLE_OUTLINED = "event_available_outlined"
        self.EVENT_BUSY_OUTLINED = "event_busy_outlined"
        self.CALENDAR_VIEW_DAY_OUTLINED = "calendar_view_day_outlined"
        self.CALENDAR_VIEW_WEEK_OUTLINED = "calendar_view_week_outlined"
        self.CALENDAR_VIEW_MONTH_OUTLINED = "calendar_view_month_outlined"
        self.SCHEDULE_SEND_OUTLINED = "schedule_send_outlined"
        self.PENDING_ACTIONS_OUTLINED = "pending_actions_outlined"
        self.FREE_CANCELLATION_OUTLINED = "free_cancellation_outlined"
        self.EVENT_SEAT_OUTLINED = "event_seat_outlined"
        self.CALL_TO_ACTION_OUTLINED = "call_to_action_outlined"
        self.BUSINESS_OUTLINED = "business_outlined"
        self.BUSINESS_CENTER_OUTLINED = "business_center_outlined"
        self.LOCATION_ON_OUTLINED = "location_on_outlined"
        self.LOCATION_OFF_OUTLINED = "location_off_outlined"
        self.MAP_OUTLINED = "map_outlined"
        self.MY_LOCATION_OUTLINED = "my_location_outlined"
        self.NAVIGATION_OUTLINED = "navigation_outlined"
        self.NEAR_ME_OUTLINED = "near_me_outlined"
        self.MAIL_OUTLINED = "mail_outlined"
        self.INBOX_OUTLINED = "inbox_outlined"
        self.OUTBOX_OUTLINED = "outbox_outlined"
        self.SEND_OUTLINED = "send_outlined"
        self.DRAFTS_OUTLINED = "drafts_outlined"
        self.ARCHIVE_OUTLINED = "archive_outlined"
        self.UNARCHIVE_OUTLINED = "unarchive_outlined"
        self.DELETE_SWEEP_OUTLINED = "delete_sweep_outlined"
        self.RESTORE_FROM_TRASH_OUTLINED = "restore_from_trash_outlined"
        self.SNOOZE_OUTLINED = "snooze_outlined"
        self.STAR_OUTLINED = "star_outlined"
        self.STAR_HALF_OUTLINED = "star_half_outlined"
        self.FLAG_OUTLINED = "flag_outlined"
        self.BOOKMARK_OUTLINED = "bookmark_outlined"
        self.LABEL_OUTLINED = "label_outlined"
        self.TAG_OUTLINED = "tag_outlined"
        self.LABELS_OUTLINED = "labels_outlined"
        self.FOLDER_SPECIAL_OUTLINED = "folder_special_outlined"
        self.ATTACHMENT_OUTLINED = "attachment_outlined"
        self.ATTACH_FILE_OUTLINED = "attach_file_outlined"
        self.ATTACH_MONEY_OUTLINED = "attach_money_outlined"
        self.LINK_OUTLINED = "link_outlined"
        self.LINK_OFF_OUTLINED = "link_off_outlined"
        self.LOW_PRIORITY_OUTLINED = "low_priority_outlined"
        self.HIGH_PRIORITY_OUTLINED = "high_priority_outlined"
        self.BLOCK_OUTLINED = "block_outlined"
        self.UNBLOCK_OUTLINED = "unblock_outlined"
        self.UNDO_OUTLINED = "undo_outlined"
        self.REDO_OUTLINED = "redo_outlined"
        self.CONTENT_COPY_OUTLINED = "content_copy_outlined"
        self.CONTENT_CUT_OUTLINED = "content_cut_outlined"
        self.CONTENT_PASTE_OUTLINED = "content_paste_outlined"
        self.SELECT_ALL_OUTLINED = "select_all_outlined"
        self.CLEAR_OUTLINED = "clear_outlined"
        self.REMOVE_CIRCLE_OUTLINED = "remove_circle_outlined"
        self.ADD_CIRCLE_OUTLINED = "add_circle_outlined"
        self.CANCEL_PRESENTATION_OUTLINED = "cancel_presentation_outlined"
        self.PAUSE_PRESENTATION_OUTLINED = "pause_presentation_outlined"
        self.STOP_SCREEN_SHARE_OUTLINED = "stop_screen_share_outlined"
        self.SECURITY_OUTLINED = "security_outlined"
        self.LOCK_OUTLINED = "lock_outlined"
        self.LOCK_OPEN_OUTLINED = "lock_open_outlined"
        self.VISIBILITY_OUTLINED = "visibility_outlined"
        self.VISIBILITY_OFF_OUTLINED = "visibility_off_outlined"
        self.KEY_OUTLINED = "key_outlined"
        self.VPN_KEY_OUTLINED = "vpn_key_outlined"
        self.SHIELD_OUTLINED = "shield_outlined"
        self.SECURITY_UPDATE_OUTLINED = "security_update_outlined"
        self.BUG_REPORT_OUTLINED = "bug_report_outlined"
        self.HELP_OUTLINED = "help_outlined"
        self.SUPPORT_OUTLINED = "support_outlined"
        self.FEEDBACK_OUTLINED = "feedback_outlined"
        self.ANNOUNCEMENT_OUTLINED = "announcement_outlined"
        self.CAMPAIGN_OUTLINED = "campaign_outlined"
        self.NOTIFICATIONS_OUTLINED = "notifications_outlined"
        self.NOTIFICATIONS_ACTIVE_OUTLINED = "notifications_active_outlined"
        self.NOTIFICATIONS_NONE_OUTLINED = "notifications_none_outlined"
        self.NOTIFICATIONS_OFF_OUTLINED = "notifications_off_outlined"
        self.NOTIFICATIONS_PAUSED_OUTLINED = "notifications_paused_outlined"
        self.DASHBOARD_OUTLINED = "dashboard_outlined"
        self.PEOPLE_OUTLINE = "people_outline"
        self.FOLDER_OUTLINED = "folder_outlined"
        self.FOLDER_OPEN_OUTLINED = "folder_open_outlined"
        self.STORAGE_OUTLINED = "storage_outlined"
        self.AUTO_GRAPH_OUTLINED = "auto_graph_outlined"
        self.ARTICLE_OUTLINED = "article_outlined"
        self.SETTINGS_OUTLINED = "settings_outlined"
        self.REFRESH_OUTLINED = "refresh_outlined"
        self.PLAY_ARROW_OUTLINED = "play_arrow_outlined"
        self.STOP_OUTLINED = "stop_outlined"
        self.BACKUP_OUTLINED = "backup_outlined"
        self.SYNC_OUTLINED = "sync_outlined"
        self.ERROR_OUTLINED = "error_outlined"
        self.WARNING_OUTLINED = "warning_outlined"
        self.INFO_OUTLINED = "info_outlined"
        self.CHECK_CIRCLE_OUTLINED = "check_circle_outlined"
        self.CANCEL_OUTLINED = "cancel_outlined"
        self.EDIT_OUTLINED = "edit_outlined"
        self.DELETE_OUTLINED = "delete_outlined"
        self.ADD_OUTLINED = "add_outlined"
        self.REMOVE_OUTLINED = "remove_outlined"
        self.SEARCH_OUTLINED = "search_outlined"
        self.FILTER_LIST_OUTLINED = "filter_list_outlined"
        self.SORT_OUTLINED = "sort_outlined"
        self.MORE_VERT_OUTLINED = "more_vert_outlined"
        self.MORE_HORIZ_OUTLINED = "more_horiz_outlined"
        self.EXPAND_MORE_OUTLINED = "expand_more_outlined"
        self.EXPAND_LESS_OUTLINED = "expand_less_outlined"
        self.KEYBOARD_ARROW_UP_OUTLINED = "keyboard_arrow_up_outlined"
        self.KEYBOARD_ARROW_DOWN_OUTLINED = "keyboard_arrow_down_outlined"
        self.KEYBOARD_ARROW_LEFT_OUTLINED = "keyboard_arrow_left_outlined"
        self.KEYBOARD_ARROW_RIGHT_OUTLINED = "keyboard_arrow_right_outlined"
        self.ARROW_UPWARD_OUTLINED = "arrow_upward_outlined"
        self.ARROW_DOWNWARD_OUTLINED = "arrow_downward_outlined"
        self.ARROW_BACK_OUTLINED = "arrow_back_outlined"
        self.ARROW_FORWARD_OUTLINED = "arrow_forward_outlined"
        self.CHEVRON_LEFT_OUTLINED = "chevron_left_outlined"
        self.CHEVRON_RIGHT_OUTLINED = "chevron_right_outlined"
        self.TRENDING_UP_OUTLINED = "trending_up_outlined"
        self.TRENDING_DOWN_OUTLINED = "trending_down_outlined"
        self.TRENDING_FLAT_OUTLINED = "trending_flat_outlined"
        self.UPDATE_OUTLINED = "update_outlined"
        self.ACCESS_TIME_OUTLINED = "access_time_outlined"
        self.CALENDAR_TODAY_OUTLINED = "calendar_today_outlined"
        self.EVENT_OUTLINED = "event_outlined"
        self.SCHEDULE_OUTLINED = "schedule_outlined"
        self.TIMER_OUTLINED = "timer_outlined"
        self.HOURGLASS_EMPTY_OUTLINED = "hourglass_empty_outlined"
        self.HOURGLASS_FULL_OUTLINED = "hourglass_full_outlined"

        # Other attributes
        self.FontWeight = self
        self.W_300 = "w300"
        self.W_400 = "w400"
        self.W_500 = "w500"
        self.W_600 = "w600"
        self.W_700 = "w700"
        self.W_BOLD = "bold"

        self.MainAxisAlignment = self
        self.START = "start"
        self.END = "end"
        self.CENTER = "center"
        self.SPACE_BETWEEN = "space_between"
        self.SPACE_AROUND = "space_around"
        self.SPACE_EVENLY = "space_evenly"

        self.CrossAxisAlignment = self
        self.STRETCH = "stretch"
        self.BASELINE = "baseline"

        self.ScrollMode = self
        self.AUTO = "auto"
        self.ALWAYS = "always"
        self.HIDDEN = "hidden"

        self.AnimationCurve = self
        self.EASE_OUT = "ease_out"
        self.EASE_IN = "ease_in"
        self.EASE_IN_OUT = "ease_in_out"
        self.EASE_OUT_BACK = "ease_out_back"
        self.EASE_IN_BACK = "ease_in_back"
        self.EASE_OUT_CUBIC = "ease_out_cubic"
        self.EASE_IN_CUBIC = "ease_in_cubic"
        self.EASE_OUT_QUART = "ease_out_quart"
        self.EASE_IN_QUART = "ease_in_quart"

        self.AnimatedSwitcherTransition = self
        self.FADE = "fade"
        self.SCALE = "scale"
        self.ROTATION = "rotation"
        self.SIZE = "size"

        self.VisualDensity = self
        self.COMPACT = "compact"
        self.COMFORTABLE = "comfortable"
        self.STANDARD = "standard"

        self.ButtonStyle = self
        self.RoundedRectangleBorder = MockControl
        self.BorderSide = MockControl

        self.padding = self
        self.symmetric = MockControl
        self.only = MockControl
        self.all = MockControl

        self.margin = self
        self.only = MockControl

        self.border = self
        self.all = MockControl

        self.border_radius = self
        self.all = MockControl

        self.BoxShadow = MockControl

        self.alignment = self
        self.center = MockControl

        self.ControlState = self
        self.DEFAULT = "default"
        self.HOVERED = "hovered"
        self.FOCUSED = "focused"
        self.PRESSED = "pressed"
        self.DISABLED = "disabled"
        self.SELECTED = "selected"
        self.ERROR = "error"

        self.NavigationRailLabelType = self
        self.NONE = "none"
        self.SELECTED = "selected"
        self.ALL = "all"

        self.AppView = self
        self.WEB_BROWSER = "web_browser"
        self.FLET_APP = "flet_app"

        self.Page = MockControl
        self.Control = MockControl
        self.AppView = self
        self.WEB_BROWSER = "web_browser"
        self.FLET_APP = "flet_app"

# Mock sys modules
# Create a proper module object and populate it with MockFlet attributes
mock_flet_module = types.ModuleType('flet')
mock_flet_instance = MockFlet()
for attr_name in dir(mock_flet_instance):
    if not attr_name.startswith('_'):  # Skip private attributes
        attr_value = getattr(mock_flet_instance, attr_name)
        setattr(mock_flet_module, attr_name, attr_value)
sys.modules['flet'] = mock_flet_module

# Mock other modules
mock_psutil_module = types.ModuleType('psutil')
mock_psutil_instance = MockPsutil()
for attr_name in dir(mock_psutil_instance):
    if not attr_name.startswith('_'):
        attr_value = getattr(mock_psutil_instance, attr_name)
        setattr(mock_psutil_module, attr_name, attr_value)
sys.modules['psutil'] = mock_psutil_module

# Mock other imports
mock_debug_setup_module = types.ModuleType('FletV2.utils.debug_setup')
setattr(mock_debug_setup_module, 'get_logger', lambda name: type('MockLogger', (), {'info': lambda *args: None, 'debug': lambda *args: None, 'warning': lambda *args: None, 'error': lambda *args: None})())
setattr(mock_debug_setup_module, 'setup_terminal_debugging', lambda logger_name: type('MockLogger', (), {'info': lambda *args: None, 'debug': lambda *args: None, 'warning': lambda *args: None, 'error': lambda *args: None})())
sys.modules['FletV2.utils.debug_setup'] = mock_debug_setup_module

mock_theme_module = types.ModuleType('FletV2.theme')
setattr(mock_theme_module, 'setup_modern_theme', lambda page: None)
sys.modules['FletV2.theme'] = mock_theme_module

mock_server_bridge_module = types.ModuleType('FletV2.utils.server_bridge')
setattr(mock_server_bridge_module, 'ServerBridge', type)
setattr(mock_server_bridge_module, 'create_server_bridge', lambda: None)
sys.modules['FletV2.utils.server_bridge'] = mock_server_bridge_module

mock_state_manager_module = types.ModuleType('FletV2.utils.state_manager')
setattr(mock_state_manager_module, 'StateManager', type)
setattr(mock_state_manager_module, 'create_state_manager', lambda page, server_bridge=None: None)
sys.modules['FletV2.utils.state_manager'] = mock_state_manager_module

mock_ui_components_module = types.ModuleType('FletV2.utils.ui_components')
setattr(mock_ui_components_module, 'themed_card', lambda **kwargs: MockControl())
setattr(mock_ui_components_module, 'create_floating_action_button', lambda **kwargs: MockControl())
setattr(mock_ui_components_module, 'create_modern_card', lambda **kwargs: MockControl())
setattr(mock_ui_components_module, 'themed_button', lambda **kwargs: MockControl())
setattr(mock_ui_components_module, 'themed_metric_card', lambda **kwargs: MockControl())
sys.modules['FletV2.utils.ui_components'] = mock_ui_components_module

mock_user_feedback_module = types.ModuleType('FletV2.utils.user_feedback')
setattr(mock_user_feedback_module, 'show_error_message', lambda *args: None)
setattr(mock_user_feedback_module, 'show_success_message', lambda *args: None)
setattr(mock_user_feedback_module, 'show_confirmation', lambda *args: None)
setattr(mock_user_feedback_module, 'show_info', lambda *args: None)
setattr(mock_user_feedback_module, 'show_info_message', lambda *args: None)
setattr(mock_user_feedback_module, 'show_input', lambda *args: None)
setattr(mock_user_feedback_module, 'show_user_feedback', lambda *args: None)
setattr(mock_user_feedback_module, 'show_warning_message', lambda *args: None)
sys.modules['FletV2.utils.user_feedback'] = mock_user_feedback_module

# Mock Shared.utils.utf8_solution
mock_utf8_solution_module = types.ModuleType('Shared.utils.utf8_solution')
setattr(mock_utf8_solution_module, 'ensure_initialized', staticmethod(lambda: None))
setattr(mock_utf8_solution_module, 'get_env', staticmethod(lambda: {}))
sys.modules['Shared.utils.utf8_solution'] = mock_utf8_solution_module

mock_shared_utils_module = types.ModuleType('Shared.utils')
setattr(mock_shared_utils_module, 'utf8_solution', mock_utf8_solution_module)
sys.modules['Shared.utils'] = mock_shared_utils_module

mock_shared_module = types.ModuleType('Shared')
setattr(mock_shared_module, 'utils', mock_shared_utils_module)
sys.modules['Shared'] = mock_shared_module

# Now try to import and test the dashboard
try:
    from FletV2.views.dashboard import create_dashboard_view
    print("✅ Successfully imported create_dashboard_view")

    # Mock page and server bridge
    mock_page = MockControl()
    mock_server_bridge = None
    mock_state_manager = None

    # Try to create the dashboard
    print("🔄 Attempting to create dashboard...")
    result = create_dashboard_view(mock_server_bridge, mock_page, mock_state_manager)  # type: ignore  # MockControl is sufficient for testing
    print(f"✅ Dashboard creation returned: {type(result)}")

    if isinstance(result, tuple) and len(result) == 3:
        dashboard_container, dispose_func, setup_func = result
        print("✅ Dashboard tuple structure is correct")
        print(f"   - Container: {type(dashboard_container)}")
        print(f"   - Dispose: {type(dispose_func)}")
        print(f"   - Setup: {type(setup_func)}")
    else:
        print(f"❌ Unexpected return type: {result}")

except Exception as e:
    print(f"❌ Error during dashboard creation: {e}")
    import traceback
    traceback.print_exc()