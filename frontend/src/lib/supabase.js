import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'yourURL';
const supabaseAnonKey = 'yourKey';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);