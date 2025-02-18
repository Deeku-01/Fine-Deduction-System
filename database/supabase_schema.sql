-- Enable the necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create VEHICLE_OWNER_HISTORY table
CREATE TABLE IF NOT EXISTS vehicle_owner_history (
    history_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id VARCHAR(36) NOT NULL,
    prev_owner_id VARCHAR(36),
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_vehicle_owner_history_vehicle_id ON vehicle_owner_history(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_vehicle_owner_history_prev_owner_id ON vehicle_owner_history(prev_owner_id);

-- Create storage buckets for images
-- Note: This needs to be done through the Supabase dashboard or API
-- vehicle_images - for storing vehicle registration images
-- challan_images - for storing violation evidence images

-- Create RLS (Row Level Security) policies
ALTER TABLE vehicle_owner_history ENABLE ROW LEVEL SECURITY;

-- Policy to allow read access to authenticated users
CREATE POLICY "Allow read access for authenticated users"
ON vehicle_owner_history
FOR SELECT
TO authenticated
USING (true);

-- Policy to allow insert access to authenticated users with admin role
CREATE POLICY "Allow insert access for admin users"
ON vehicle_owner_history
FOR INSERT
TO authenticated
WITH CHECK (
    EXISTS (
        SELECT 1 FROM auth.users
        WHERE auth.users.id = auth.uid()
        AND auth.users.role = 'admin'
    )
); 