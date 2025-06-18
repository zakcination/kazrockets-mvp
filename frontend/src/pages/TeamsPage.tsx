import React from 'react'
import { Users, Plus } from 'lucide-react'

const TeamsPage: React.FC = () => {
  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Teams</h1>
          <p className="mt-2 text-gray-600">
            Manage and view robotics competition teams
          </p>
        </div>
        <button className="btn btn-primary btn-md">
          <Plus className="h-4 w-4 mr-2" />
          Create Team
        </button>
      </div>

      <div className="card">
        <div className="card-body">
          <div className="text-center py-12">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No teams yet</h3>
            <p className="text-gray-500 mb-4">
              Get started by creating your first team or joining an existing one.
            </p>
            <button className="btn btn-primary btn-md">
              <Plus className="h-4 w-4 mr-2" />
              Create your first team
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TeamsPage