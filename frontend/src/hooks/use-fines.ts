import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fineApi, Fine, ApiResponse } from '@/lib/api'

export const useFinesQuery = (params?: any) => {
  return useQuery({
    queryKey: ['fines', params],
    queryFn: () => fineApi.list(params),
  })
}

export const useFineQuery = (id: string) => {
  return useQuery({
    queryKey: ['fine', id],
    queryFn: () => fineApi.get(id),
    enabled: !!id,
  })
}

export const useMarkAsPaidMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => fineApi.markAsPaid(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fines'] })
    },
  })
}

export const useUnpaidFinesQuery = (params?: any) => {
  return useQuery({
    queryKey: ['unpaidFines', params],
    queryFn: () => fineApi.unpaid(params),
  })
}
