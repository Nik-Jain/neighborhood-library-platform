import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { borrowingApi, Borrowing, ApiResponse } from '@/lib/api'

export const useBorrowingsQuery = (params?: any) => {
  return useQuery({
    queryKey: ['borrowings', params],
    queryFn: () => borrowingApi.list(params),
  })
}

export const useBorrowingQuery = (id: string) => {
  return useQuery({
    queryKey: ['borrowing', id],
    queryFn: () => borrowingApi.get(id),
    enabled: !!id,
  })
}

export const useCreateBorrowingMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: any) => borrowingApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['borrowings'] })
      queryClient.invalidateQueries({ queryKey: ['books'] })
      queryClient.invalidateQueries({ queryKey: ['members'] })
    },
  })
}

export const useReturnBookMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => borrowingApi.returnBook(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['borrowing', id] })
      queryClient.invalidateQueries({ queryKey: ['borrowings'] })
      queryClient.invalidateQueries({ queryKey: ['books'] })
      queryClient.invalidateQueries({ queryKey: ['members'] })
      queryClient.invalidateQueries({ queryKey: ['fines'] })
    },
  })
}

export const useOverdueBorrowingsQuery = (params?: any) => {
  return useQuery({
    queryKey: ['overdueBorrowings', params],
    queryFn: () => borrowingApi.overdue(params),
  })
}

export const useActiveBorrowingsQuery = (params?: any) => {
  return useQuery({
    queryKey: ['activeBorrowings', params],
    queryFn: () => borrowingApi.active(params),
  })
}
