'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { AlertCircle, Loader } from 'lucide-react'
import { useCreateMemberMutation } from '@/hooks/use-members'
import { useAuthStore } from '@/store/auth'

export default function NewMemberPage() {
  const router = useRouter()
  const { isAdminOrLibrarian } = useAuthStore()
  const createMember = useCreateMemberMutation()

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    address: '',
    membership_status: 'active',
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [generalError, setGeneralError] = useState('')

  if (!isAdminOrLibrarian()) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900">Access denied</h1>
        <p className="text-gray-600 mt-2">Only admins or librarians can add members.</p>
        <Link href="/members" className="text-primary-600 hover:text-primary-700 mt-4 inline-block">
          Back to Members
        </Link>
      </div>
    )
  }

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }))
    }
  }

  const validate = () => {
    const nextErrors: Record<string, string> = {}
    if (!formData.first_name.trim()) nextErrors.first_name = 'First name is required'
    if (!formData.last_name.trim()) nextErrors.last_name = 'Last name is required'
    if (!formData.email.trim()) nextErrors.email = 'Email is required'
    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setGeneralError('')

    if (!validate()) return

    try {
      await createMember.mutateAsync({
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim(),
        email: formData.email.trim(),
        phone: formData.phone || undefined,
        address: formData.address || undefined,
        membership_status: formData.membership_status as any,
      })
      router.push('/members')
    } catch (err: any) {
      const data = err?.response?.data
      if (data && typeof data === 'object') {
        const nextErrors: Record<string, string> = {}
        Object.keys(data).forEach((key) => {
          const messages = Array.isArray(data[key]) ? data[key] : [data[key]]
          nextErrors[key] = messages.join(', ')
        })
        setErrors(nextErrors)
      } else {
        setGeneralError('Failed to create member. Please try again.')
      }
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Add Member</h1>
        <Link href="/members" className="text-primary-600 hover:text-primary-700">
          Back to Members
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        {generalError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3 mb-6">
            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
            <p className="text-red-700 text-sm">{generalError}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">First Name *</label>
              <input
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                className={`w-full px-4 py-2 border rounded-lg ${errors.first_name ? 'border-red-500' : 'border-gray-300'}`}
                required
              />
              {errors.first_name && (
                <p className="text-red-600 text-xs mt-1">{errors.first_name}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Last Name *</label>
              <input
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                className={`w-full px-4 py-2 border rounded-lg ${errors.last_name ? 'border-red-500' : 'border-gray-300'}`}
                required
              />
              {errors.last_name && (
                <p className="text-red-600 text-xs mt-1">{errors.last_name}</p>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
            <input
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              className={`w-full px-4 py-2 border rounded-lg ${errors.email ? 'border-red-500' : 'border-gray-300'}`}
              required
            />
            {errors.email && <p className="text-red-600 text-xs mt-1">{errors.email}</p>}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
              <input
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg border-gray-300"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Membership Status</label>
              <select
                name="membership_status"
                value={formData.membership_status}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg border-gray-300"
              >
                <option value="active">Active</option>
                <option value="suspended">Suspended</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
            <textarea
              name="address"
              value={formData.address}
              onChange={handleChange}
              rows={3}
              className="w-full px-4 py-2 border rounded-lg border-gray-300"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Membership Number</label>
            <p className="text-sm text-gray-600">Auto-assigned after creation</p>
          </div>

          <button
            type="submit"
            disabled={createMember.isPending}
            className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 flex items-center gap-2 disabled:opacity-50"
          >
            {createMember.isPending && <Loader className="w-4 h-4 animate-spin" />}
            Create Member
          </button>
        </form>
      </div>
    </div>
  )
}
