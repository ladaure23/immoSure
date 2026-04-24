import axios from "axios";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const { data } = await axios.post<LoginResponse>("/api/auth/login", payload);
  return data;
}
