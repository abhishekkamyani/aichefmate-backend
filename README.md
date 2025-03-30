## Setup
1. Create `.env` file:
   ```env
   SECRET_KEY=your_flask_secret_key
   
   SUPABASE_URL=https://your-project-ref.supabase.co

   JWT_AUDIENCE=authenticated
   
   JWT_ISSUER=https://your-project-ref.supabase.co/auth/v1

2. Install Dependencies
    ``` 
    pip install -r requirements.txt
3. Run
    ```
    python run.py