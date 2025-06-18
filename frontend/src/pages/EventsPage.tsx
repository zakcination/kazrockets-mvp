import React from 'react'
import { Calendar, Plus } from 'lucide-react'

const EventsPage: React.FC = () => {
  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Events</h1>
          <p className="mt-2 text-gray-600">
            View and manage robotics competition events
          </p>
        </div>
        <button className="btn btn-primary btn-md">
          <Plus className="h-4 w-4 mr-2" />
          Create Event
        </button>
      </div>

      <div className="card">
        <div className="card-body">
          <div className="text-center py-12">
            <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No events yet</h3>
            <p className="text-gray-500 mb-4">
              Create your first robotics competition event to get started.
            </p>
            <button className="btn btn-primary btn-md">
              <Plus className="h-4 w-4 mr-2" />
              Create your first event
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EventsPage