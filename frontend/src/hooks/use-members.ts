import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { memberApi, Member, ApiResponse } from '@/lib/api'

export const useMembersQuery = (params?: any) => {
  return useQuery({
    queryKey: ['members', params],
    queryFn: () => memberApi.list(params),
  })
}

export const useMemberQuery = (id: string) => {
  return useQuery({
    queryKey: ['member', id],
    queryFn: () => memberApi.get(id),
    enabled: !!id,
  })
}

export const useCreateMemberMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: any) => memberApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['members'] })
    },
  })
}

export const useUpdateMemberMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      memberApi.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['member', id] })
      queryClient.invalidateQueries({ queryKey: ['members'] })
    },
  })
}

export const useDeleteMemberMutation = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => memberApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['members'] })
    },
  })
}

export const useMemberBorrowingHistoryQuery = (id: string, params?: any) => {
  return useQuery({
    queryKey: ['memberBorrowingHistory', id, params],
    queryFn: () => memberApi.borrowingHistory(id, params),
    enabled: !!id,
  })
}

export const useMemberActiveBorrowingsQuery = (id: string) => {
  return useQuery({
    queryKey: ['memberActiveBorrowings', id],
    queryFn: () => memberApi.activeBorrowings(id),
    enabled: !!id,
  })
}
