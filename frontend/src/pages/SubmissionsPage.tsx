import React from 'react'
import { FileText, Upload } from 'lucide-react'

const SubmissionsPage: React.FC = () => {
  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Submissions</h1>
          <p className="mt-2 text-gray-600">
            Manage project submissions for competitions
          </p>
        </div>
        <button className="btn btn-primary btn-md">
          <Upload className="h-4 w-4 mr-2" />
          Upload Submission
        </button>
      </div>

      <div className="card">
        <div className="card-body">
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No submissions yet</h3>
            <p className="text-gray-500 mb-4">
              Upload your first project submission to participate in competitions.
            </p>
            <button className="btn btn-primary btn-md">
              <Upload className="h-4 w-4 mr-2" />
              Upload your first submission
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SubmissionsPage