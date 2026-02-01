'use client'

import { useEffect, useState } from 'react'
import { useCurrentMemberQuery, useUpdateMemberMutation, useChangePasswordMutation, useMemberActiveBorrowingsQuery, useMemberBorrowingHistoryQuery } from '@/hooks/use-members'
import { User, Lock, BookOpen, AlertCircle, CheckCircle, AlertTriangle } from 'lucide-react'

export default function ProfilePage() {
  const { data: memberResponse, isLoading, isError } = useCurrentMemberQuery()
  const member = memberResponse?.data
  const updateMember = useUpdateMemberMutation()
  const changePassword = useChangePasswordMutation()
  
  const [activeTab, setActiveTab] = useState<'profile' | 'borrowings' | 'fines' | 'password'>('profile')
  const [editMode, setEditMode] = useState(false)
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    address: '',
  })
  const [passwordForm, setPasswordForm] = useState({
    old_password: '',
    new_password: '',
    new_password_confirm: '',
  })
  const [successMessage, setSuccessMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')

  // Fetch member's borrowings
  const { isLoading: borrowingsLoading } = useMemberActiveBorrowingsQuery(
    member?.id || '',
  )
  const { data: borrowingHistoryResponse, isLoading: historyLoading } = useMemberBorrowingHistoryQuery(
    member?.id || '',
    { page: 1, page_size: 10 },
  )

  useEffect(() => {
    if (!member) return
    setFormData({
      first_name: member.first_name || '',
      last_name: member.last_name || '',
      email: member.email || '',
      phone: member.phone || '',
      address: member.address || '',
    })
  }, [member])

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-gray-500">Loading profile...</div>
      </div>
    )
  }

  if (isError || !member) {
    return (
      <div className="space-y-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="font-medium text-red-900">Error Loading Profile</h3>
            <p className="text-red-700 text-sm mt-1">Failed to load your profile. Please try again later.</p>
          </div>
        </div>
      </div>
    )
  }

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    setSuccessMessage('')
    setErrorMessage('')

    try {
      await updateMember.mutateAsync({
        id: member.id,
        data: formData,
      })
      setSuccessMessage('Profile updated successfully!')
      setEditMode(false)
      setTimeout(() => setSuccessMessage(''), 3000)
    } catch (error: any) {
      const errorMsg = error?.response?.data?.error || 'Failed to update profile'
      setErrorMessage(errorMsg)
    }
  }

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()
    setSuccessMessage('')
    setErrorMessage('')

    if (!member?.id) {
      setErrorMessage('Profile not loaded. Please try again.')
      return
    }

    if (passwordForm.new_password !== passwordForm.new_password_confirm) {
      setErrorMessage('New passwords do not match')
      return
    }

    if (passwordForm.new_password.length < 6) {
      setErrorMessage('New password must be at least 6 characters long')
      return
    }

    try {
      await changePassword.mutateAsync({
        id: member.id,
        data: {
          old_password: passwordForm.old_password,
          new_password: passwordForm.new_password,
          new_password_confirm: passwordForm.new_password_confirm,
        },
      })
      setSuccessMessage('Password changed successfully!')
      setPasswordForm({
        old_password: '',
        new_password: '',
        new_password_confirm: '',
      })
      setTimeout(() => setSuccessMessage(''), 3000)
    } catch (error: any) {
      const errorMsg = error?.response?.data?.error || 'Failed to change password'
      setErrorMessage(errorMsg)
    }
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData({ ...formData, [field]: value })
  }

  const handlePasswordInputChange = (field: string, value: string) => {
    setPasswordForm({ ...passwordForm, [field]: value })
  }

  // Calculate fines from borrowings
  const borrowings = borrowingHistoryResponse?.data?.results || []
  const fines = borrowings
    .filter(b => b.fine && !b.fine.is_paid)
    .map(b => ({
      id: b.fine?.id || '',
      book_title: b.book_title,
      amount: b.fine?.amount || '0',
      reason: b.fine?.reason || '',
      is_paid: b.fine?.is_paid || false,
    }))

  const totalUnpaidFines = fines.reduce((sum, fine) => sum + (parseFloat(fine.amount) || 0), 0)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
      </div>

      {successMessage && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
          <p className="text-green-700">{successMessage}</p>
        </div>
      )}

      {errorMessage && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
          <p className="text-red-700">{errorMessage}</p>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200 bg-white rounded-lg">
        <div className="flex gap-8 px-6">
          <button
            onClick={() => setActiveTab('profile')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'profile'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <User className="w-4 h-4 inline mr-2" />
            Profile
          </button>
          <button
            onClick={() => setActiveTab('borrowings')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'borrowings'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <BookOpen className="w-4 h-4 inline mr-2" />
            Borrowings
          </button>
          <button
            onClick={() => setActiveTab('fines')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'fines'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <AlertTriangle className="w-4 h-4 inline mr-2" />
            Fines
          </button>
          <button
            onClick={() => setActiveTab('password')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'password'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Lock className="w-4 h-4 inline mr-2" />
            Security
          </button>
        </div>
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="space-y-6">
            {/* Membership Info */}
            <div className="border-b pb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Membership Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Membership Number</label>
                  <p className="text-gray-900">{member.membership_number}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                  <p className="text-gray-900 capitalize">
                    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                      member.membership_status === 'active'
                        ? 'bg-green-100 text-green-800'
                        : member.membership_status === 'suspended'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {member.membership_status}
                    </span>
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Join Date</label>
                  <p className="text-gray-900">{new Date(member.join_date).toLocaleDateString()}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Active Borrowings</label>
                  <p className="text-gray-900">{member.active_borrowings_count}</p>
                </div>
              </div>
            </div>

            {/* Personal Details */}
            {!editMode ? (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">Personal Details</h2>
                  <button
                    onClick={() => {
                      setEditMode(true)
                      setFormData({
                        first_name: member.first_name,
                        last_name: member.last_name,
                        email: member.email,
                        phone: member.phone || '',
                        address: member.address || '',
                      })
                    }}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
                  >
                    Edit
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                    <p className="text-gray-900">{member.first_name}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                    <p className="text-gray-900">{member.last_name}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <p className="text-gray-900">{member.email}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                    <p className="text-gray-900">{member.phone || 'Not provided'}</p>
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                    <p className="text-gray-900">{member.address || 'Not provided'}</p>
                  </div>
                </div>
              </div>
            ) : (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">Edit Personal Details</h2>
                </div>
                <form onSubmit={handleProfileUpdate} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                      <input
                        type="text"
                        value={formData.first_name}
                        onChange={(e) => handleInputChange('first_name', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                      <input
                        type="text"
                        value={formData.last_name}
                        onChange={(e) => handleInputChange('last_name', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                      <input
                        type="email"
                        value={formData.email}
                        onChange={(e) => handleInputChange('email', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                      <input
                        type="tel"
                        value={formData.phone}
                        onChange={(e) => handleInputChange('phone', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      />
                    </div>
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                      <textarea
                        value={formData.address}
                        onChange={(e) => handleInputChange('address', e.target.value)}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      />
                    </div>
                  </div>
                  <div className="flex gap-3 pt-4">
                    <button
                      type="submit"
                      disabled={updateMember.isPending}
                      className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium disabled:opacity-50"
                    >
                      {updateMember.isPending ? 'Saving...' : 'Save Changes'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setEditMode(false)}
                      className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Borrowings Tab */}
      {activeTab === 'borrowings' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">My Borrowings</h2>
          
          {historyLoading ? (
            <div className="text-center py-8 text-gray-500">Loading borrowings...</div>
          ) : borrowings.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No borrowings found</div>
          ) : (
            <div className="space-y-4">
              {borrowings.map((borrowing) => (
                <div key={borrowing.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-600">Book Title</label>
                      <p className="text-gray-900 font-medium">{borrowing.book_title}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">Status</label>
                      <p className={`font-medium ${
                        borrowing.status === 'returned'
                          ? 'text-gray-600'
                          : borrowing.status === 'overdue'
                          ? 'text-red-600'
                          : 'text-green-600'
                      }`}>
                        {borrowing.status.toUpperCase()}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">Borrowed On</label>
                      <p className="text-gray-900">{new Date(borrowing.borrowed_at).toLocaleDateString()}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">Due Date</label>
                      <p className={borrowing.is_overdue && !borrowing.returned_at ? 'text-red-600 font-medium' : 'text-gray-900'}>
                        {new Date(borrowing.due_date).toLocaleDateString()}
                      </p>
                    </div>
                    {borrowing.returned_at && (
                      <div>
                        <label className="text-sm font-medium text-gray-600">Returned On</label>
                        <p className="text-gray-900">{new Date(borrowing.returned_at).toLocaleDateString()}</p>
                      </div>
                    )}
                    {borrowing.days_until_due !== null && borrowing.days_until_due !== undefined && (
                      <div>
                        <label className="text-sm font-medium text-gray-600">Days Until Due</label>
                        <p className={borrowing.days_until_due < 0 ? 'text-red-600 font-medium' : 'text-gray-900'}>
                          {borrowing.days_until_due} days
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Fines Tab */}
      {activeTab === 'fines' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">My Fines</h2>
          
          {historyLoading ? (
            <div className="text-center py-8 text-gray-500">Loading fines...</div>
          ) : fines.length === 0 ? (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center text-green-700">
              <CheckCircle className="w-6 h-6 inline mr-2" />
              No outstanding fines
            </div>
          ) : (
            <div className="space-y-4">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                <p className="text-red-900 font-medium">
                  Total Unpaid Fines: <span className="text-lg">${totalUnpaidFines.toFixed(2)}</span>
                </p>
              </div>
              {fines.map((fine) => (
                <div key={fine.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-600">Book Title</label>
                      <p className="text-gray-900 font-medium">{fine.book_title}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">Amount</label>
                      <p className="text-gray-900 font-medium">${parseFloat(fine.amount).toFixed(2)}</p>
                    </div>
                    <div className="md:col-span-2">
                      <label className="text-sm font-medium text-gray-600">Reason</label>
                      <p className="text-gray-900">{fine.reason}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Password Tab */}
      {activeTab === 'password' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Change Password</h2>
          <form onSubmit={handlePasswordChange} className="max-w-md space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Current Password</label>
              <input
                type="password"
                value={passwordForm.old_password}
                onChange={(e) => handlePasswordInputChange('old_password', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">New Password</label>
              <input
                type="password"
                value={passwordForm.new_password}
                onChange={(e) => handlePasswordInputChange('new_password', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
              <p className="text-xs text-gray-500 mt-1">Must be at least 6 characters long</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Confirm New Password</label>
              <input
                type="password"
                value={passwordForm.new_password_confirm}
                onChange={(e) => handlePasswordInputChange('new_password_confirm', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>
            <button
              type="submit"
              disabled={changePassword.isPending}
              className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium disabled:opacity-50 mt-6"
            >
              {changePassword.isPending ? 'Changing Password...' : 'Change Password'}
            </button>
          </form>
        </div>
      )}
    </div>
  )
}
