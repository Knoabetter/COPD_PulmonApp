import { useState } from 'react';
import { Stethoscope, ChevronDown } from 'lucide-react';

// Diagnostic Criteria Buttons Component
// inline=true: renders just the dropdown grid with no outer card/header
const DiagnosticCriteriaButtons = ({ onCriteriaSelect, compact = false, inline = false }) => {
  const [openDropdown, setOpenDropdown] = useState(null);
  const [selectedCriteria, setSelectedCriteria] = useState<Record<string, string>>({});

  const criteriaOptions = {
    restrictive: {
      title: 'Restrictive patterns',
      options: [
        'No restrictive ventilatory defect',
        'Mild restrictive ventilatory defect',
        'Moderate restrictive ventilatory defect',
        'Severe restrictive ventilatory defect'
      ]
    },
    obstructive: {
      title: 'Obstructive patterns',
      options: [
        'No obstructive ventilatory defect',
        'Mild obstructive ventilatory defect',
        'Moderate obstructive ventilatory defect',
        'Moderate–severe obstructive ventilatory defect',
        'Severe obstructive ventilatory defect',
        'Very severe obstructive ventilatory defect'
      ]
    },
    bronchodilator: {
      title: 'Bronchodilator response',
      options: [
        'No significant bronchodilator response',
        'Partial bronchodilator response',
        'Significant (positive) bronchodilator response',
        'Bronchodilators not used/administrated'
      ]
    },
    lungVolumes: {
      title: 'Lung volumes',
      options: [
        'Lung volumes within normal limits',
        'Reduced lung volumes; body plethysmography is recommended'
      ]
    },
    airTrapping: {
      title: 'Air trapping',
      options: [
        'No air trapping present',
        'Air trapping present',
        'Severe air trapping'
      ]
    },
    diffusion: {
      title: 'Diffusion capacity (DLCO / KCO)',
      options: [
        'Preserved diffusion capacity',
        'Mildly reduced diffusion capacity',
        'Moderately reduced diffusion capacity',
        'Severely reduced diffusion capacity'
      ]
    },
    dlcoCorrection: {
      title: 'DLCO correction for alveolar volume',
      options: [
        'Diffusion capacity normalizes after correction for alveolar volume (KCO normal)',
        'Partial improvement in diffusion capacity after correction for alveolar volume',
        'No improvement in diffusion capacity after correction for alveolar volume'
      ]
    }
  };

  const handleOptionSelect = (category, option) => {
    const newSelection = { ...selectedCriteria, [category]: option };
    setSelectedCriteria(newSelection);
    setOpenDropdown(null);
    if (onCriteriaSelect) {
      onCriteriaSelect(newSelection);
    }
  };

  const toggleDropdown = (category) => {
    setOpenDropdown(openDropdown === category ? null : category);
  };

  const getSeverityColor = (option) => {
    if (option.toLowerCase().includes('no ') || option.toLowerCase().includes('normal') || option.toLowerCase().includes('preserved')) {
      return 'text-green-600';
    } else if (option.toLowerCase().includes('mild')) {
      return 'text-yellow-600';
    } else if (option.toLowerCase().includes('moderate')) {
      return 'text-orange-600';
    } else if (option.toLowerCase().includes('severe')) {
      return 'text-red-600';
    }
    return 'text-gray-700';
  };

  const isCompact = compact || inline;

  const dropdownGrid = (
    <div className={`grid grid-cols-1 md:grid-cols-2 ${isCompact ? 'gap-2' : 'gap-3'}`}>
      {Object.entries(criteriaOptions).map(([key, criteria]) => (
        <div key={key} className="relative">
          <button
            onClick={() => toggleDropdown(key)}
            className={`w-full text-left ${isCompact ? 'px-3 py-2' : 'px-4 py-3'} bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all`}
          >
            <div className="flex items-center justify-between">
              <span className={`font-medium text-gray-700 ${isCompact ? 'text-sm' : ''}`}>{criteria.title}</span>
              <ChevronDown
                className={`${isCompact ? 'w-4 h-4' : 'w-5 h-5'} text-gray-500 transform transition-transform ${
                  openDropdown === key ? 'rotate-180' : ''
                }`}
              />
            </div>
            {selectedCriteria[key] && (
              <p className={`${isCompact ? 'text-xs' : 'text-sm'} mt-1 truncate ${getSeverityColor(selectedCriteria[key])}`}>
                {selectedCriteria[key]}
              </p>
            )}
          </button>

          {openDropdown === key && (
            <div className="absolute z-10 mt-2 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
              {criteria.options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => handleOptionSelect(key, option)}
                  className={`w-full text-left ${isCompact ? 'px-3 py-2' : 'px-4 py-3'} hover:bg-gray-50 transition-colors border-b last:border-b-0 ${
                    selectedCriteria[key] === option ? 'bg-blue-50' : ''
                  }`}
                >
                  <span className={`${isCompact ? 'text-xs' : 'text-sm'} ${getSeverityColor(option)}`}>
                    {option}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );

  if (inline) return dropdownGrid;

  return (
    <div className={`bg-white border rounded-lg ${compact ? 'p-4' : 'p-6'}`}>
      <h3 className={`${compact ? 'text-md' : 'text-lg'} font-semibold text-gray-900 mb-4 flex items-center`}>
        <Stethoscope className="w-5 h-5 mr-2" />
        Diagnostic Criteria Selection
      </h3>
      {dropdownGrid}
    </div>
  );
};

export default DiagnosticCriteriaButtons;
