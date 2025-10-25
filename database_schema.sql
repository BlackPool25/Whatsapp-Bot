-- Create detection_history table
CREATE TABLE IF NOT EXISTS detection_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID,  -- NULL for anonymous WhatsApp users, populated for logged-in web users
    session_id TEXT,  -- WhatsApp phone number or temporary session identifier for anonymous users
    file_url TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,  -- 'image', 'video', 'document'
    file_size BIGINT NOT NULL,
    file_extension TEXT NOT NULL,
    detection_result TEXT,  -- Result of deepfake detection (e.g., 'authentic', 'fake', 'uncertain')
    confidence_score DECIMAL(5,2),  -- Confidence score (0.00 to 100.00)
    is_file_available BOOLEAN DEFAULT TRUE,
    file_deleted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on user_id for faster queries (allows NULL values)
CREATE INDEX IF NOT EXISTS idx_detection_history_user_id ON detection_history(user_id) WHERE user_id IS NOT NULL;

-- Create index on session_id for anonymous user queries
CREATE INDEX IF NOT EXISTS idx_detection_history_session_id ON detection_history(session_id) WHERE session_id IS NOT NULL;

-- Create composite index for anonymous users (user_id IS NULL and session_id exists)
CREATE INDEX IF NOT EXISTS idx_detection_history_anonymous ON detection_history(session_id) WHERE user_id IS NULL;

-- Create index on created_at for cleanup operations and ordering
CREATE INDEX IF NOT EXISTS idx_detection_history_created_at ON detection_history(created_at DESC);

-- Create index on is_file_available for filtering
CREATE INDEX IF NOT EXISTS idx_detection_history_is_file_available ON detection_history(is_file_available);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_detection_history_updated_at BEFORE UPDATE
    ON detection_history FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- Add constraint to ensure either user_id or session_id is present
ALTER TABLE detection_history 
ADD CONSTRAINT check_user_or_session 
CHECK (user_id IS NOT NULL OR session_id IS NOT NULL);

-- Optional: Add RLS (Row Level Security) policies
-- ALTER TABLE detection_history ENABLE ROW LEVEL SECURITY;

-- Example policy for authenticated users to see only their own records
-- CREATE POLICY "Users can view their own detection history"
--     ON detection_history FOR SELECT
--     USING (
--         (auth.uid() IS NOT NULL AND auth.uid() = user_id) OR 
--         (auth.uid() IS NULL AND session_id IS NOT NULL)
--     );

-- Example policy for inserting records
-- CREATE POLICY "Users can insert their own detection history"
--     ON detection_history FOR INSERT
--     WITH CHECK (
--         (auth.uid() IS NOT NULL AND auth.uid() = user_id) OR 
--         (auth.uid() IS NULL AND session_id IS NOT NULL)
--     );
