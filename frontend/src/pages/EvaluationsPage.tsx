import React from 'react'
import { Award, Star } from 'lucide-react'

const EvaluationsPage: React.FC = () => {
  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Evaluations</h1>
          <p className="mt-2 text-gray-600">
            Review and evaluate project submissions
          </p>
        </div>
        <button className="btn btn-primary btn-md">
          <Star className="h-4 w-4 mr-2" />
          Start Evaluation
        </button>
      </div>

      <div className="card">
        <div className="card-body">
          <div className="text-center py-12">
            <Award className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No evaluations yet</h3>
            <p className="text-gray-500 mb-4">
              Start evaluating project submissions to help determine competition winners.
            </p>
            <button className="btn btn-primary btn-md">
              <Star className="h-4 w-4 mr-2" />
              Start your first evaluation
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EvaluationsPage