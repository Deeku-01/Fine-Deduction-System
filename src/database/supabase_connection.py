from supabase import create_client, Client
from config.config import SUPABASE_URL, SUPABASE_KEY

class SupabaseConnection:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseConnection, cls).__new__(cls)
            cls._instance._client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return cls._instance

    @property
    def client(self) -> Client:
        return self._client

    def get_vehicle_history(self, vehicle_id: str):
        """Get vehicle ownership history"""
        return self.client.table('vehicle_owner_history')\
            .select('*')\
            .eq('vehicle_id', vehicle_id)\
            .order('start_date', desc=True)\
            .execute()

    def add_vehicle_history(self, vehicle_id: str, prev_owner_id: str, start_date: str, end_date: str = None):
        """Add new vehicle ownership history record"""
        return self.client.table('vehicle_owner_history')\
            .insert({
                'vehicle_id': vehicle_id,
                'prev_owner_id': prev_owner_id,
                'start_date': start_date,
                'end_date': end_date
            })\
            .execute()

    def upload_image(self, bucket: str, file_path: str, file_name: str):
        """Upload image to Supabase storage"""
        with open(file_path, 'rb') as f:
            return self.client.storage\
                .from_(bucket)\
                .upload(file_name, f)

    def get_image_url(self, bucket: str, file_name: str):
        """Get public URL for an uploaded image"""
        return self.client.storage\
            .from_(bucket)\
            .get_public_url(file_name)

# Usage example:
# supabase = SupabaseConnection().client
# history = supabase.get_vehicle_history('vehicle-123') 