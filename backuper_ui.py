from PyQt5.Qt import *

config_path = './config/config.yml'
pid_path = './pid'


class BackupUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IncreBackup")
        self.resize(400, 600)

        vBox = QVBoxLayout()
        self.setLayout(vBox)
        self.backup_ui(vBox)
        self.source_ui(vBox)
        self.time_ui(vBox)
        hBox = QHBoxLayout()
        vBox.addLayout(hBox)
        self.filter_iu(hBox)
        self.log_ui(hBox)
        vBox.addStretch(0)
        self.btns_ui(vBox)

    def backup_ui(self, parent):

        hBox = QHBoxLayout()
        gBox = QGroupBox('backup to:')
        hBox_in_gBox = QHBoxLayout()

        self.line_edit = QLineEdit()
        if self.opt['backup_root']:
            self.line_edit.setText(self.opt['backup_root'])
        self.line_edit.setReadOnly(True)
        hBox_in_gBox.addWidget(self.line_edit)

        chang_path_btn = QToolButton()
        chang_path_btn.clicked.connect(self.get_backup_root)
        hBox_in_gBox.addWidget(chang_path_btn)
        gBox.setLayout(hBox_in_gBox)
        hBox.addWidget(gBox)

        parent.addLayout(hBox)

    def source_ui(self, parent):
        hBox = QHBoxLayout()
        gBox = QGroupBox('sources:')
        vBox_in_gBox = QVBoxLayout()

        sources_list = ('a', 'b', 'c', 'a1', 'b1', 'c1', 'a2', 'b2', 'c2')
        sources_data_model = QStringListModel()
        sources_data_model.setStringList(sources_list)
        sources_list_view = QListView()
        sources_list_view.setModel(sources_data_model)
        sources_list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        sources_list_view.customContextMenuRequested[QPoint].connect(self.listWidgetContext)
        vBox_in_gBox.addWidget(sources_list_view)

        gBox.setLayout(vBox_in_gBox)
        hBox.addWidget(gBox)
        parent.addLayout(hBox)

    def time_ui(self, parent):
        hBox = QHBoxLayout()
        gBox = QGroupBox('time:')
        hBox_in_gBox = QHBoxLayout()

        label1 = QLabel()
        label1.setText('每隔')
        hBox_in_gBox.addWidget(label1)

        line_edit = QLineEdit()
        line_edit.setText('10')
        line_edit.setMaximumWidth(50)
        intValidator = QIntValidator(self)
        intValidator.setRange(1, 99)
        line_edit.setValidator(intValidator)
        hBox_in_gBox.addWidget(line_edit)

        commbox = QComboBox()
        commbox.addItems(['秒', '分钟', '小时', '天'])
        hBox_in_gBox.addWidget(commbox)

        label2 = QLabel()
        label2.setText('执行备份')
        hBox_in_gBox.addWidget(label2)
        hBox_in_gBox.addStretch(1)

        edit_btn = QPushButton()
        edit_btn.setText('修改')
        hBox_in_gBox.addWidget(edit_btn)

        gBox.setLayout(hBox_in_gBox)
        hBox.addWidget(gBox)
        parent.addLayout(hBox)

    def filter_iu(self, parent):
        hBox = QHBoxLayout()
        gBox = QGroupBox('filter:')
        vBox_in_gBox = QVBoxLayout()

        filter_list = ('*.log', '*.lock', '*.bin', '*.obj', '*/tmp/*', '*/.vscode/*')
        filter_data_model = QStringListModel()
        filter_data_model.setStringList(filter_list)
        filter_list_view = QListView()
        filter_list_view.setModel(filter_data_model)
        filter_list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        filter_list_view.customContextMenuRequested[QPoint].connect(self.listWidgetContext)
        vBox_in_gBox.addWidget(filter_list_view)

        gBox.setLayout(vBox_in_gBox)
        gBox.setMaximumWidth(200)
        hBox.addWidget(gBox)
        parent.addLayout(hBox)

    def log_ui(self, parent):
        hBox = QHBoxLayout()
        gBox = QGroupBox('time interval:')
        vBox_in_gBox = QVBoxLayout()

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setText('''fdsafdsafdsa
fdsafdsafdsa
fdsafdsafdsafdsafdsa
fdsavcxzvcxzv
federfdsacvdxzdfds
vcdafdsafdsa
fdsafdsafdsa''')

        vBox_in_gBox.addWidget(text_edit)
        gBox.setLayout(vBox_in_gBox)
        hBox.addWidget(gBox)
        parent.addLayout(hBox)

    def listWidgetContext(self, point):
        popMenu = QMenu()
        popMenu.addAction("添加")
        popMenu.addAction("删除")
        popMenu.exec_(QCursor.pos())

    def btns_ui(self, parent):
        hBox = QHBoxLayout()

        refresh_btn = QPushButton()
        refresh_btn.setMinimumHeight(40)
        refresh_btn.setText('刷新状态')
        manual_btn = QPushButton()
        manual_btn.setMinimumHeight(40)
        manual_btn.setText('手动执行')
        auto_btn = QPushButton()
        auto_btn.setMinimumHeight(40)
        auto_btn.setText('自动执行')
        stop_btn = QPushButton()
        stop_btn.setMinimumHeight(40)
        stop_btn.setText('停止自动备份')
        hBox.addStretch(1)
        hBox.addWidget(refresh_btn)
        hBox.addWidget(manual_btn)
        hBox.addWidget(auto_btn)
        hBox.addWidget(stop_btn)

        parent.addLayout(hBox)

    def get_backup_root(self):
        directory = QFileDialog.getExistingDirectory(None, "选取备份根目录", "C:/")  # 起始路径
        if directory:
            self.line_edit.setText(directory)
