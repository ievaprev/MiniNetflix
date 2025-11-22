USE mini_netflix;

-- Audito lentelės
CREATE TABLE IF NOT EXISTS system_audit (
    user_id text,
    event_time timestamp,
    action text,
    details text,
    PRIMARY KEY ((user_id), event_time)
) WITH CLUSTERING ORDER BY (event_time DESC);


CREATE TABLE IF NOT EXISTS system_audit_by_time (
    event_date text,
    event_time timestamp,
    user_id text,
    action text,
    details text,
    PRIMARY KEY ((event_date), event_time)
) WITH CLUSTERING ORDER BY (event_time DESC);



-- Chat lentelės
CREATE TABLE IF NOT EXISTS chats_by_user (
    user_id text,
    chat_id uuid,
    started_at timestamp,
    last_timestamp timestamp,
    title text,
    PRIMARY KEY ((user_id), last_msg_at, chat_id)
) WITH CLUSTERING ORDER BY (last_msg_at DESC);

CREATE TABLE IF NOT EXISTS chat_messages (
    chat_id uuid,
    ts timestamp,
    sender text, 
    message text,
    PRIMARY KEY ((chat_id), ts)
) WITH CLUSTERING ORDER BY (ts ASC);