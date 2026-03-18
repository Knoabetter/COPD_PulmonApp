export type StatusChip = { text: string; class: string };

export const formatValue = (value: number | null | undefined, digits = 3): string => {
  if (value == null) return '-';
  if (Number.isNaN(value)) return '-';
  return value.toFixed(digits);
};

export const getStatus = (
  measured: number | null | undefined,
  predicted: number | null | undefined
): StatusChip => {
  if (measured == null || predicted == null || Number.isNaN(measured) || Number.isNaN(predicted) || predicted === 0) {
    return { text: 'N/A', class: 'bg-gray-100 text-gray-800' };
  }

  const percentage = (measured / predicted) * 100;
  if (percentage >= 80) return { text: 'Normal', class: 'bg-green-100 text-green-800' };
  if (percentage >= 60) return { text: 'Mild', class: 'bg-yellow-100 text-yellow-800' };
  return { text: 'Abnormal', class: 'bg-red-100 text-red-800' };
};

export const getSeverityColor = (severity?: string | null): string => {
  switch (severity?.toLowerCase()) {
    case 'normal':
      return 'bg-green-100 text-green-800 border-green-200';
    case 'mild':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'moderate':
      return 'bg-orange-100 text-orange-800 border-orange-200';
    case 'severe':
      return 'bg-red-100 text-red-800 border-red-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

export const getColorClass = (
  measured: number | null | undefined,
  predicted: number | null | undefined
): string => {
  if (measured == null || predicted == null || Number.isNaN(measured) || Number.isNaN(predicted) || predicted === 0) {
    return 'text-gray-500';
  }

  const ratio = measured / predicted;
  if (ratio >= 0.8) return 'text-green-600 font-semibold';
  if (ratio >= 0.6) return 'text-yellow-600 font-semibold';
  return 'text-red-600 font-semibold';
};
