import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { bookApi, Book, ApiResponse } from '@/lib/api'

export const useBooksQuery = (params?: any) => {
  return useQuery({
    queryKey: ['books', params],
    queryFn: () => bookApi.list(params),
  })
}

export const useBookQuery = (id: string) => {
  return useQuery({
    queryKey: ['book', id],
    queryFn: () => bookApi.get(id),
    enabled: !!id,
  })
}

export const useCreateBookMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: any) => bookApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['books'] })
    },
  })
}

export const useUpdateBookMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      bookApi.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['book', id] })
      queryClient.invalidateQueries({ queryKey: ['books'] })
    },
  })
}

export const useDeleteBookMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => bookApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['books'] })
    },
  })
}

export const useIncreaseCopiesMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, quantity }: { id: string; quantity: number }) =>
      bookApi.increaseCopies(id, quantity),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['book', id] })
      queryClient.invalidateQueries({ queryKey: ['books'] })
    },
  })
}

export const useBookBorrowingHistoryQuery = (id: string, params?: any) => {
  return useQuery({
    queryKey: ['bookBorrowingHistory', id, params],
    queryFn: () => bookApi.borrowingHistory(id, params),
    enabled: !!id,
  })
}
