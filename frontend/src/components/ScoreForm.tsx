import { useState, useEffect } from 'react';
import type {
  ProductInput,
  MaterialInput,
  MaterialReference,
  OriginReference,
  CareReference,
  CertificationReference,
} from '../types';
import { getMaterials, getOrigins, getCareInstructions, getCertifications } from '../api/client';

interface ScoreFormProps {
  onSubmit: (product: ProductInput) => void;
  isLoading?: boolean;
}

export function ScoreForm({ onSubmit, isLoading }: ScoreFormProps) {
  const [materials, setMaterials] = useState<MaterialReference[]>([]);
  const [origins, setOrigins] = useState<OriginReference[]>([]);
  const [careInstructions, setCareInstructions] = useState<CareReference[]>([]);
  const [certifications, setCertifications] = useState<CertificationReference[]>([]);
  const [loadingRef, setLoadingRef] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [brand, setBrand] = useState('');
  const [category, setCategory] = useState('Other');
  const [subcategory, setSubcategory] = useState('Other');
  const [productMaterials, setProductMaterials] = useState<MaterialInput[]>([
    { name: '', percentage: 100 },
  ]);
  const [origin, setOrigin] = useState('');
  const [careInstruction, setCareInstruction] = useState('');
  const [cert1, setCert1] = useState('No Certification');
  const [cert2, setCert2] = useState('No Certification');

  useEffect(() => {
    async function loadReferenceData() {
      try {
        const [mats, origs, care, certs] = await Promise.all([
          getMaterials(),
          getOrigins(),
          getCareInstructions(),
          getCertifications(),
        ]);
        setMaterials(mats);
        setOrigins(origs);
        setCareInstructions(care);
        setCertifications(certs);

        // Set defaults after loading
        if (origs.length > 0) setOrigin(origs[0].name);
        if (care.length > 0) setCareInstruction(care[0].name);
        if (mats.length > 0) {
          setProductMaterials([{ name: mats[0].name, percentage: 100 }]);
        }
      } catch (error) {
        console.error('Failed to load reference data:', error);
        setLoadError('Failed to load reference data. Make sure the API is running.');
      } finally {
        setLoadingRef(false);
      }
    }
    loadReferenceData();
  }, []);

  const addMaterial = () => {
    const defaultName = materials.length > 0 ? materials[0].name : '';
    setProductMaterials([...productMaterials, { name: defaultName, percentage: 0 }]);
  };

  const removeMaterial = (index: number) => {
    if (productMaterials.length > 1) {
      setProductMaterials(productMaterials.filter((_, i) => i !== index));
    }
  };

  const updateMaterial = (index: number, field: keyof MaterialInput, value: string | number) => {
    const updated = [...productMaterials];
    if (field === 'percentage') {
      updated[index][field] = Number(value);
    } else {
      updated[index][field] = value as string;
    }
    setProductMaterials(updated);
  };

  const totalPercentage = productMaterials.reduce((sum, m) => sum + m.percentage, 0);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (productMaterials.some(m => !m.name)) {
      alert('Please select all materials');
      return;
    }

    if (Math.abs(totalPercentage - 100) > 0.01) {
      alert('Material percentages must sum to 100%');
      return;
    }

    // Generate a descriptive product name from materials
    const materialNames = productMaterials
      .filter(m => m.percentage > 0)
      .sort((a, b) => b.percentage - a.percentage)
      .map(m => m.name)
      .slice(0, 2)
      .join('/');
    const generatedName = `${materialNames} ${subcategory}`;

    const product: ProductInput = {
      product_name: generatedName,
      brand: brand || 'Unknown',
      category,
      subcategory,
      materials: productMaterials,
      origin,
      care_instruction: careInstruction,
      certification1: cert1,
      certification2: cert2,
    };

    onSubmit(product);
  };

  if (loadingRef) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="p-6 bg-gray-100 text-gray-700 rounded-lg">
        <p className="font-medium mb-2">Error Loading Form</p>
        <p className="text-sm">{loadError}</p>
        <p className="text-sm mt-2">
          Run: <code className="bg-gray-200 px-1 rounded">make dev-backend</code>
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Product Details */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Product Details</h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Brand
            </label>
            <input
              type="text"
              value={brand}
              onChange={(e) => setBrand(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              placeholder="e.g., Patagonia"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent bg-white"
            >
              <option value="Woman">Woman</option>
              <option value="Man">Man</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Subcategory
            </label>
            <input
              type="text"
              value={subcategory}
              onChange={(e) => setSubcategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              placeholder="e.g., T-shirt, Jumper"
            />
          </div>
        </div>
      </div>

      {/* Materials */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Materials</h3>
          <span className={`text-sm font-medium ${Math.abs(totalPercentage - 100) < 0.01 ? 'text-gray-600' : 'text-gray-900'}`}>
            Total: {totalPercentage}%
          </span>
        </div>

        {productMaterials.map((material, index) => (
          <div key={index} className="flex gap-3 mb-3">
            <div className="flex-1">
              <select
                value={material.name}
                onChange={(e) => updateMaterial(index, 'name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent bg-white"
              >
                {materials.map((m) => (
                  <option key={m.name} value={m.name}>
                    {m.name} ({m.category})
                  </option>
                ))}
              </select>
            </div>
            <div className="w-24">
              <input
                type="number"
                min="0"
                max="100"
                value={material.percentage}
                onChange={(e) => updateMaterial(index, 'percentage', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              />
            </div>
            <span className="py-2 text-gray-500">%</span>
            {productMaterials.length > 1 && (
              <button
                type="button"
                onClick={() => removeMaterial(index)}
                className="px-3 py-2 text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Remove
              </button>
            )}
          </div>
        ))}

        <button
          type="button"
          onClick={addMaterial}
          className="mt-2 text-sm text-gray-600 hover:text-gray-900 font-medium"
        >
          + Add Another Material
        </button>
      </div>

      {/* Origin & Care */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Manufacturing & Care</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Manufacturing Origin *
            </label>
            <select
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent bg-white"
              required
            >
              {origins.map((o) => (
                <option key={o.name} value={o.name}>
                  {o.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Care Instruction *
            </label>
            <select
              value={careInstruction}
              onChange={(e) => setCareInstruction(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent bg-white"
              required
            >
              {careInstructions.map((c) => (
                <option key={c.name} value={c.name}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Certifications */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Certifications</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Certification 1
            </label>
            <select
              value={cert1}
              onChange={(e) => setCert1(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent bg-white"
            >
              {certifications.map((c) => (
                <option key={c.name} value={c.name}>
                  {c.name} {c.score_bonus > 0 && `(+${(c.score_bonus * 100).toFixed(0)}%)`}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Certification 2
            </label>
            <select
              value={cert2}
              onChange={(e) => setCert2(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent bg-white"
            >
              {certifications.map((c) => (
                <option key={c.name} value={c.name}>
                  {c.name} {c.score_bonus > 0 && `(+${(c.score_bonus * 100).toFixed(0)}%)`}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-3 px-6 bg-gray-900 text-white font-medium rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? 'Calculating...' : 'Calculate Sustainability Score'}
      </button>
    </form>
  );
}
