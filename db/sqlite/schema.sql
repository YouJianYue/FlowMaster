-- SQLite版本的表结构定义
-- 转换自MySQL main_table.sql

-- 菜单表
CREATE TABLE IF NOT EXISTS sys_menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    parent_id INTEGER NOT NULL DEFAULT 0,
    type INTEGER NOT NULL DEFAULT 1, -- 类型（1：目录；2：菜单；3：按钮）
    path TEXT DEFAULT NULL,
    name TEXT DEFAULT NULL,
    component TEXT DEFAULT NULL,
    redirect TEXT DEFAULT NULL,
    icon TEXT DEFAULT NULL,
    is_external INTEGER DEFAULT 0, -- 是否外链
    is_cache INTEGER DEFAULT 0, -- 是否缓存
    is_hidden INTEGER DEFAULT 0, -- 是否隐藏
    permission TEXT DEFAULT NULL,
    sort INTEGER NOT NULL DEFAULT 999,
    status INTEGER NOT NULL DEFAULT 1, -- 状态（1：启用；2：禁用）
    create_user INTEGER NOT NULL,
    create_time TEXT NOT NULL,
    update_user INTEGER DEFAULT NULL,
    update_time TEXT DEFAULT NULL
);

-- 菜单表索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_menu_title_parent_id ON sys_menu(title, parent_id);
CREATE INDEX IF NOT EXISTS idx_menu_parent_id ON sys_menu(parent_id);
CREATE INDEX IF NOT EXISTS idx_menu_create_user ON sys_menu(create_user);
CREATE INDEX IF NOT EXISTS idx_menu_update_user ON sys_menu(update_user);

-- 部门表
CREATE TABLE IF NOT EXISTS sys_dept (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER NOT NULL DEFAULT 0,
    ancestors TEXT NOT NULL DEFAULT '',
    description TEXT DEFAULT NULL,
    sort INTEGER NOT NULL DEFAULT 999,
    status INTEGER NOT NULL DEFAULT 1, -- 状态（1：启用；2：禁用）
    is_system INTEGER NOT NULL DEFAULT 0, -- 是否为系统内置数据
    create_user INTEGER NOT NULL,
    create_time TEXT NOT NULL,
    update_user INTEGER DEFAULT NULL,
    update_time TEXT DEFAULT NULL
);

-- 部门表索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_dept_name_parent_id ON sys_dept(name, parent_id);
CREATE INDEX IF NOT EXISTS idx_dept_parent_id ON sys_dept(parent_id);
CREATE INDEX IF NOT EXISTS idx_dept_create_user ON sys_dept(create_user);
CREATE INDEX IF NOT EXISTS idx_dept_update_user ON sys_dept(update_user);

-- 角色表
CREATE TABLE IF NOT EXISTS sys_role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    data_scope TEXT NOT NULL DEFAULT 'SELF', -- 数据权限（ALL：全部数据权限；DEPT_AND_CHILD：本部门及以下数据权限；DEPT：本部门数据权限；SELF：仅本人数据权限；CUSTOM：自定义数据权限）
    description TEXT DEFAULT NULL,
    sort INTEGER NOT NULL DEFAULT 999,
    is_system INTEGER NOT NULL DEFAULT 0, -- 是否为系统内置数据
    menu_check_strictly INTEGER DEFAULT 1, -- 菜单选择是否父子节点关联
    dept_check_strictly INTEGER DEFAULT 1, -- 部门选择是否父子节点关联
    create_user INTEGER NOT NULL,
    create_time TEXT NOT NULL,
    update_user INTEGER DEFAULT NULL,
    update_time TEXT DEFAULT NULL
);

-- 角色表索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_role_name ON sys_role(name);
CREATE UNIQUE INDEX IF NOT EXISTS uk_role_code ON sys_role(code);
CREATE INDEX IF NOT EXISTS idx_role_create_user ON sys_role(create_user);
CREATE INDEX IF NOT EXISTS idx_role_update_user ON sys_role(update_user);

-- 用户表
CREATE TABLE IF NOT EXISTS sys_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    nickname TEXT NOT NULL,
    password TEXT DEFAULT NULL,
    gender INTEGER NOT NULL DEFAULT 0, -- 性别（0：未知；1：男；2：女）
    email TEXT DEFAULT NULL,
    phone TEXT DEFAULT NULL,
    avatar TEXT DEFAULT NULL,
    description TEXT DEFAULT NULL,
    status INTEGER NOT NULL DEFAULT 1, -- 状态（1：启用；2：禁用）
    is_system INTEGER NOT NULL DEFAULT 0, -- 是否为系统内置数据
    pwd_reset_time TEXT DEFAULT NULL,
    dept_id INTEGER NOT NULL,
    create_user INTEGER DEFAULT NULL,
    create_time TEXT NOT NULL,
    update_user INTEGER DEFAULT NULL,
    update_time TEXT DEFAULT NULL
);

-- 用户表索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_user_username ON sys_user(username);
CREATE UNIQUE INDEX IF NOT EXISTS uk_user_email ON sys_user(email);
CREATE UNIQUE INDEX IF NOT EXISTS uk_user_phone ON sys_user(phone);
CREATE INDEX IF NOT EXISTS idx_user_dept_id ON sys_user(dept_id);
CREATE INDEX IF NOT EXISTS idx_user_create_user ON sys_user(create_user);
CREATE INDEX IF NOT EXISTS idx_user_update_user ON sys_user(update_user);

-- 用户历史密码表
CREATE TABLE IF NOT EXISTS sys_user_password_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    password TEXT NOT NULL,
    create_time TEXT NOT NULL
);

-- 用户历史密码表索引
CREATE INDEX IF NOT EXISTS idx_user_password_history_user_id ON sys_user_password_history(user_id);

-- 用户社会化关联表
CREATE TABLE IF NOT EXISTS sys_user_social (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    open_id TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    meta_json TEXT DEFAULT NULL,
    last_login_time TEXT DEFAULT NULL,
    create_time TEXT NOT NULL
);

-- 用户社会化关联表索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_user_social_source_open_id ON sys_user_social(source, open_id);

-- 用户和角色关联表
CREATE TABLE IF NOT EXISTS sys_user_role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL
);

-- 用户和角色关联表索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_user_role_user_id_role_id ON sys_user_role(user_id, role_id);

-- 角色和菜单关联表
CREATE TABLE IF NOT EXISTS sys_role_menu (
    role_id INTEGER NOT NULL,
    menu_id INTEGER NOT NULL,
    PRIMARY KEY (role_id, menu_id)
);

-- 角色和部门关联表
CREATE TABLE IF NOT EXISTS sys_role_dept (
    role_id INTEGER NOT NULL,
    dept_id INTEGER NOT NULL,
    PRIMARY KEY (role_id, dept_id)
);

-- 参数表
CREATE TABLE IF NOT EXISTS sys_option (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    value TEXT DEFAULT NULL,
    default_value TEXT DEFAULT NULL,
    description TEXT DEFAULT NULL,
    update_user INTEGER DEFAULT NULL,
    update_time TEXT DEFAULT NULL
);

-- 参数表索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_option_category_code ON sys_option(category, code);

-- 字典表
CREATE TABLE IF NOT EXISTS sys_dict (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    description TEXT DEFAULT NULL,
    is_system INTEGER NOT NULL DEFAULT 0, -- 是否为系统内置数据
    create_user INTEGER NOT NULL,
    create_time TEXT NOT NULL,
    update_user INTEGER DEFAULT NULL,
    update_time TEXT DEFAULT NULL
);

-- 字典表索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_dict_name ON sys_dict(name);
CREATE UNIQUE INDEX IF NOT EXISTS uk_dict_code ON sys_dict(code);

-- 字典项表
CREATE TABLE IF NOT EXISTS sys_dict_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL,
    value TEXT NOT NULL,
    color TEXT DEFAULT NULL,
    sort INTEGER NOT NULL DEFAULT 999,
    description TEXT DEFAULT NULL,
    status INTEGER NOT NULL DEFAULT 1, -- 状态（1：启用；2：禁用）
    dict_id INTEGER NOT NULL,
    create_user INTEGER NOT NULL,
    create_time TEXT NOT NULL,
    update_user INTEGER DEFAULT NULL,
    update_time TEXT DEFAULT NULL
);

-- 字典项表索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_dict_item_value_dict_id ON sys_dict_item(value, dict_id);
CREATE INDEX IF NOT EXISTS idx_dict_item_dict_id ON sys_dict_item(dict_id);
CREATE INDEX IF NOT EXISTS idx_dict_item_create_user ON sys_dict_item(create_user);
CREATE INDEX IF NOT EXISTS idx_dict_item_update_user ON sys_dict_item(update_user);

-- 系统日志表
CREATE TABLE IF NOT EXISTS sys_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id TEXT DEFAULT NULL,
    description TEXT NOT NULL,
    module TEXT NOT NULL,
    request_url TEXT NOT NULL,
    request_method TEXT NOT NULL,
    request_headers TEXT DEFAULT NULL,
    request_body TEXT DEFAULT NULL,
    status_code INTEGER NOT NULL,
    response_headers TEXT DEFAULT NULL,
    response_body TEXT DEFAULT NULL,
    time_taken INTEGER NOT NULL, -- 耗时（ms）
    ip TEXT DEFAULT NULL,
    address TEXT DEFAULT NULL,
    browser TEXT DEFAULT NULL,
    os TEXT DEFAULT NULL,
    status INTEGER NOT NULL DEFAULT 1, -- 状态（1：成功；2：失败）
    error_msg TEXT DEFAULT NULL,
    create_user INTEGER DEFAULT NULL,
    create_time TEXT NOT NULL
);

-- 系统日志表索引
CREATE INDEX IF NOT EXISTS idx_log_module ON sys_log(module);
CREATE INDEX IF NOT EXISTS idx_log_ip ON sys_log(ip);
CREATE INDEX IF NOT EXISTS idx_log_address ON sys_log(address);
CREATE INDEX IF NOT EXISTS idx_log_create_time ON sys_log(create_time);

-- 消息表
CREATE TABLE IF NOT EXISTS sys_message (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT DEFAULT NULL,
    type INTEGER NOT NULL DEFAULT 1, -- 类型（1：系统消息；2：安全消息）
    path TEXT DEFAULT NULL,
    scope INTEGER NOT NULL DEFAULT 1, -- 通知范围（1：所有人；2：指定用户）
    users TEXT DEFAULT NULL, -- JSON格式的通知用户
    create_time TEXT NOT NULL
);

-- 消息日志表
CREATE TABLE IF NOT EXISTS sys_message_log (
    message_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    read_time TEXT DEFAULT NULL,
    PRIMARY KEY (message_id, user_id)
);

-- 公告表
CREATE TABLE IF NOT EXISTS sys_notice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    type TEXT NOT NULL,
    notice_scope INTEGER NOT NULL DEFAULT 1, -- 通知范围（1：所有人；2：指定用户）
    notice_users TEXT DEFAULT NULL, -- JSON格式的通知用户
    notice_methods TEXT DEFAULT NULL, -- JSON格式的通知方式（1：系统消息；2：登录弹窗）
    is_timing INTEGER NOT NULL DEFAULT 0, -- 是否定时
    publish_time TEXT DEFAULT NULL,
    is_top INTEGER NOT NULL DEFAULT 0, -- 是否置顶
    status INTEGER NOT NULL DEFAULT 1, -- 状态（1：草稿；2：待发布；3：已发布）
    create_user INTEGER NOT NULL,
    create_time TEXT NOT NULL,
    update_user INTEGER DEFAULT NULL,
    update_time TEXT DEFAULT NULL
);

-- 公告表索引
CREATE INDEX IF NOT EXISTS idx_notice_create_user ON sys_notice(create_user);
CREATE INDEX IF NOT EXISTS idx_notice_update_user ON sys_notice(update_user);

-- 公告日志表
CREATE TABLE IF NOT EXISTS sys_notice_log (
    notice_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    read_time TEXT DEFAULT NULL,
    PRIMARY KEY (notice_id, user_id)
);

-- 存储表
CREATE TABLE IF NOT EXISTS sys_storage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    type INTEGER NOT NULL DEFAULT 1, -- 类型（1：本地存储；2：对象存储）
    access_key TEXT DEFAULT NULL,
    secret_key TEXT DEFAULT NULL,
    endpoint TEXT DEFAULT NULL,
    bucket_name TEXT NOT NULL,
    domain TEXT DEFAULT NULL,
    description TEXT DEFAULT NULL,
    is_default INTEGER NOT NULL DEFAULT 0, -- 是否为默认存储
    sort INTEGER NOT NULL DEFAULT 999,
    status INTEGER NOT NULL DEFAULT 1, -- 状态（1：启用；2：禁用）
    create_user INTEGER NOT NULL,
    create_time TEXT NOT NULL,
    update_user INTEGER DEFAULT NULL,
    update_time TEXT DEFAULT NULL
);

-- 存储表索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_storage_code ON sys_storage(code);
CREATE INDEX IF NOT EXISTS idx_storage_create_user ON sys_storage(create_user);
CREATE INDEX IF NOT EXISTS idx_storage_update_user ON sys_storage(update_user);

-- 文件表
CREATE TABLE IF NOT EXISTS sys_file (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    original_name TEXT NOT NULL,
    size INTEGER DEFAULT NULL, -- 大小（字节）
    parent_path TEXT NOT NULL DEFAULT '/',
    path TEXT NOT NULL,
    extension TEXT DEFAULT NULL,
    content_type TEXT DEFAULT NULL,
    type INTEGER NOT NULL DEFAULT 1, -- 类型（0: 目录；1：其他；2：图片；3：文档；4：视频；5：音频）
    sha256 TEXT DEFAULT NULL,
    metadata TEXT DEFAULT NULL,
    thumbnail_name TEXT DEFAULT NULL,
    thumbnail_size INTEGER DEFAULT NULL, -- 缩略图大小（字节)
    thumbnail_metadata TEXT DEFAULT NULL,
    storage_id INTEGER NOT NULL,
    create_user INTEGER NOT NULL,
    create_time TEXT NOT NULL,
    update_user INTEGER DEFAULT NULL,
    update_time TEXT DEFAULT NULL
);

-- 文件表索引
CREATE INDEX IF NOT EXISTS idx_file_type ON sys_file(type);
CREATE INDEX IF NOT EXISTS idx_file_sha256 ON sys_file(sha256);
CREATE INDEX IF NOT EXISTS idx_file_storage_id ON sys_file(storage_id);
CREATE INDEX IF NOT EXISTS idx_file_create_user ON sys_file(create_user);

-- 客户端表
CREATE TABLE IF NOT EXISTS sys_client (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id TEXT NOT NULL,
    client_type TEXT NOT NULL,
    auth_type TEXT NOT NULL, -- JSON格式的认证类型
    active_timeout INTEGER DEFAULT -1, -- Token最低活跃频率（单位：秒，-1：不限制，永不冻结）
    timeout INTEGER DEFAULT 2592000, -- Token有效期（单位：秒，-1：永不过期）
    status INTEGER NOT NULL DEFAULT 1, -- 状态（1：启用；2：禁用）
    create_user INTEGER NOT NULL,
    create_time TEXT NOT NULL,
    update_user INTEGER DEFAULT NULL,
    update_time TEXT DEFAULT NULL
);

-- 客户端表索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_client_client_id ON sys_client(client_id);
CREATE INDEX IF NOT EXISTS idx_client_create_user ON sys_client(create_user);
CREATE INDEX IF NOT EXISTS idx_client_update_user ON sys_client(update_user);

-- 短信配置表
CREATE TABLE IF NOT EXISTS sys_sms_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    supplier TEXT NOT NULL,
    access_key TEXT NOT NULL,
    secret_key TEXT NOT NULL,
    signature TEXT DEFAULT NULL,
    template_id TEXT DEFAULT NULL,
    weight INTEGER DEFAULT NULL,
    retry_interval INTEGER DEFAULT NULL,
    max_retries INTEGER DEFAULT NULL,
    maximum INTEGER DEFAULT NULL,
    supplier_config TEXT DEFAULT NULL,
    is_default INTEGER NOT NULL DEFAULT 0, -- 是否为默认配置
    status INTEGER NOT NULL DEFAULT 1, -- 状态（1：启用；2：禁用）
    create_user INTEGER NOT NULL,
    create_time TEXT NOT NULL,
    update_user INTEGER DEFAULT NULL,
    update_time TEXT DEFAULT NULL
);

-- 短信配置表索引
CREATE INDEX IF NOT EXISTS idx_sms_config_create_user ON sys_sms_config(create_user);
CREATE INDEX IF NOT EXISTS idx_sms_config_update_user ON sys_sms_config(update_user);

-- 短信日志表
CREATE TABLE IF NOT EXISTS sys_sms_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_id INTEGER NOT NULL,
    phone TEXT NOT NULL,
    params TEXT DEFAULT NULL,
    status INTEGER NOT NULL DEFAULT 1, -- 发送状态（1：成功；2：失败）
    res_msg TEXT DEFAULT NULL,
    create_user INTEGER NOT NULL,
    create_time TEXT NOT NULL
);

-- 短信日志表索引
CREATE INDEX IF NOT EXISTS idx_sms_log_config_id ON sys_sms_log(config_id);
CREATE INDEX IF NOT EXISTS idx_sms_log_create_user ON sys_sms_log(create_user);