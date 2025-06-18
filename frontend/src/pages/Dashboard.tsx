import React from 'react'
import { useAuth } from '../hooks/useAuth'
import { Users, Calendar, FileText, Award } from 'lucide-react'

const Dashboard: React.FC = () => {
  const { user } = useAuth()

  const stats = [
    {
      name: 'Total Teams',
      value: '12',
      icon: Users,
      color: 'text-blue-600 bg-blue-100',
    },
    {
      name: 'Active Events',
      value: '3',
      icon: Calendar,
      color: 'text-green-600 bg-green-100',
    },
    {
      name: 'Submissions',
      value: '48',
      icon: FileText,
      color: 'text-purple-600 bg-purple-100',
    },
    {
      name: 'Evaluations',
      value: '156',
      icon: Award,
      color: 'text-orange-600 bg-orange-100',
    },
  ]

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.name}!
        </h1>
        <p className="mt-2 text-gray-600">
          Here's what's happening with your robotics competitions today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.name} className="card">
              <div className="card-body">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className={`p-3 rounded-lg ${stat.color}`}>
                      <Icon className="h-6 w-6" />
                    </div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">
                      {stat.name}
                    </p>
                    <p className="text-2xl font-bold text-gray-900">
                      {stat.value}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Activity */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                    <FileText className="h-4 w-4 text-green-600" />
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-900">New submission from Team Rockets</p>
                  <p className="text-xs text-gray-500">2 minutes ago</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <Users className="h-4 w-4 text-blue-600" />
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-900">Team Alpha joined competition</p>
                  <p className="text-xs text-gray-500">1 hour ago</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 bg-purple-100 rounded-full flex items-center justify-center">
                    <Award className="h-4 w-4 text-purple-600" />
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-900">Evaluation completed for Project X</p>
                  <p className="text-xs text-gray-500">3 hours ago</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
          </div>
          <div className="card-body">
            <div className="space-y-3">
              {user?.role === 'ORGANIZER' && (
                <button className="btn btn-primary btn-md w-full justify-start">
                  <Calendar className="h-4 w-4 mr-2" />
                  Create New Event
                </button>
              )}
              
              {user?.role === 'PARTICIPANT' && (
                <>
                  <button className="btn btn-primary btn-md w-full justify-start">
                    <Users className="h-4 w-4 mr-2" />
                    Create Team
                  </button>
                  <button className="btn btn-outline btn-md w-full justify-start">
                    <FileText className="h-4 w-4 mr-2" />
                    Submit Project
                  </button>
                </>
              )}
              
              {user?.role === 'JUDGE' && (
                <button className="btn btn-primary btn-md w-full justify-start">
                  <Award className="h-4 w-4 mr-2" />
                  Start Evaluation
                </button>
              )}
              
              <button className="btn btn-secondary btn-md w-full justify-start">
                <Calendar className="h-4 w-4 mr-2" />
                View All Events
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard