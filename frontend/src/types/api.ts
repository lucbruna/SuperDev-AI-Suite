export interface ApiResponse<T> {
  data: T;
  message: string;
  status: number;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  message: string;
  status: number;
  timestamp: string;
  pagination: PaginationMeta;
}

export interface PaginationMeta {
  page: number;
  limit: number;
  totalItems: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPrevPage: boolean;
}

export interface ApiError {
  message: string;
  status: number;
  errors?: FieldError[];
  timestamp: string;
  path?: string;
}

export interface FieldError {
  field: string;
  message: string;
  code: string;
}

export interface QueryParams {
  page?: number;
  limit?: number;
  search?: string;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
  [key: string]: unknown;
}

export type RequestStatus = "idle" | "loading" | "success" | "error";
