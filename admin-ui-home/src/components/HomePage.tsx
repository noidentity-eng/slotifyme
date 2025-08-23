import React, { useState } from 'react';
import { Scissors, Users, Calendar, Plus, Settings, LogOut, User, CreditCard } from 'lucide-react';

interface Plan {
  id: string;
  name: string;
  price: number;
  duration: string;
  features: string[];
  isActive: boolean;
}

interface Tenant {
  id: string;
  name: string;
  email: string;
  phone: string;
  plan: string;
  status: 'active' | 'inactive' | 'pending';
  joinDate: string;
}

const HomePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'plans' | 'tenants'>('plans');
  const [showNewPlanForm, setShowNewPlanForm] = useState(false);
  const [showNewTenantForm, setShowNewTenantForm] = useState(false);

  // Sample data
  const [plans] = useState<Plan[]>([
    {
      id: '1',
      name: 'Basic Cut',
      price: 25,
      duration: '30 min',
      features: ['Haircut', 'Wash', 'Style'],
      isActive: true
    },
    {
      id: '2',
      name: 'Premium Package',
      price: 45,
      duration: '60 min',
      features: ['Haircut', 'Wash', 'Style', 'Beard Trim', 'Hot Towel'],
      isActive: true
    },
    {
      id: '3',
      name: 'Deluxe Experience',
      price: 75,
      duration: '90 min',
      features: ['Haircut', 'Wash', 'Style', 'Beard Trim', 'Hot Towel', 'Scalp Massage', 'Face Treatment'],
      isActive: false
    }
  ]);

  const [tenants] = useState<Tenant[]>([
    {
      id: '1',
      name: 'John Smith',
      email: 'john@email.com',
      phone: '(555) 123-4567',
      plan: 'Premium Package',
      status: 'active',
      joinDate: '2024-01-15'
    },
    {
      id: '2',
      name: 'Mike Johnson',
      email: 'mike@email.com',
      phone: '(555) 987-6543',
      plan: 'Basic Cut',
      status: 'active',
      joinDate: '2024-02-20'
    },
    {
      id: '3',
      name: 'David Wilson',
      email: 'david@email.com',
      phone: '(555) 456-7890',
      plan: 'Deluxe Experience',
      status: 'pending',
      joinDate: '2024-03-10'
    }
  ]);

  const tabs = [
    {
      id: 'plans',
      label: 'Manage Plans',
      icon: CreditCard,
      description: 'Manage service plans and pricing'
    },
    {
      id: 'tenants',
      label: 'Manage Tenants',
      icon: Users,
      description: 'Manage customers and memberships'
    }
  ];

  const renderPlansContent = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Service Plans</h2>
          <p className="text-gray-600 mt-1">Manage your barbershop service offerings</p>
        </div>
        <button
          onClick={() => setShowNewPlanForm(true)}
          className="text-white px-4 py-2 rounded-lg font-semibold hover:opacity-90 transition-all duration-200 flex items-center space-x-2 transform hover:scale-105"
          style={{background: 'linear-gradient(to right, #b17a50, #c8855c)'}}
        >
          <Plus className="w-4 h-4" />
          <span>New Plan</span>
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Plan Name
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Duration
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Features
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {plans.map((plan) => (
                <tr key={plan.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="font-semibold text-gray-900">{plan.name}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-2xl font-bold" style={{color: '#b17a50'}}>${plan.price}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-gray-900">{plan.duration}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="space-y-1">
                      {plan.features.map((feature, index) => (
                        <div key={index} className="flex items-center space-x-2">
                          <div className="w-2 h-2 rounded-full" style={{backgroundColor: '#b17a50'}}></div>
                          <span className="text-gray-700 text-sm">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        plan.isActive
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {plan.isActive ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-3">
                      <button 
                        className="text-xl hover:scale-110 transition-transform duration-200"
                        title="Edit plan"
                      >
                        ⚙️
                      </button>
                      <button 
                        className="text-xl hover:scale-110 transition-transform duration-200"
                        title="Archive plan"
                      >
                        📦
                      </button>
                      <button 
                        className="text-xl hover:scale-110 transition-transform duration-200"
                        title={plan.isActive ? "Deactivate plan" : "Activate plan"}
                      >
                        {plan.isActive ? '🔴' : '🟢'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderTenantsContent = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Customer Management</h2>
          <p className="text-gray-600 mt-1">Manage your customers and their memberships</p>
        </div>
        <button
          onClick={() => setShowNewTenantForm(true)}
          className="text-white px-4 py-2 rounded-lg font-semibold hover:opacity-90 transition-all duration-200 flex items-center space-x-2 transform hover:scale-105"
          style={{background: 'linear-gradient(to right, #b17a50, #c8855c)'}}
        >
          <Plus className="w-4 h-4" />
          <span>New Customer</span>
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Customer
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Contact
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Plan
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Join Date
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {tenants.map((tenant) => (
                <tr key={tenant.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{background: 'linear-gradient(to right, #b17a50, #c8855c)'}}>
                        <User className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900">{tenant.name}</div>
                        <div className="text-gray-500 text-sm">ID: {tenant.id}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-gray-900">{tenant.email}</div>
                    <div className="text-gray-500 text-sm">{tenant.phone}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-3 py-1 rounded-full text-sm font-medium text-white" style={{backgroundColor: '#b17a50'}}>
                      {tenant.plan}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        tenant.status === 'active'
                          ? 'bg-green-100 text-green-800'
                          : tenant.status === 'pending'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {tenant.status.charAt(0).toUpperCase() + tenant.status.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-gray-900">
                    {new Date(tenant.joinDate).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-3">
                      <button 
                        className="text-xl hover:scale-110 transition-transform duration-200"
                        title="Edit customer"
                      >
                        ⚙️
                      </button>
                      <button 
                        className="text-xl hover:scale-110 transition-transform duration-200"
                        title="Remove customer"
                      >
                        ❌
                      </button>
                      <button 
                        className="text-xl hover:scale-110 transition-transform duration-200"
                        title="View profile"
                      >
                        🔍
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen w-full relative" style={{background: '#1a012b'}}>
      <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width=%22100%22 height=%22100%22 viewBox=%220 0 100 100%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cdefs%3E%3Cpattern id=%22darkTexture%22 x=%220%22 y=%220%22 width=%2250%22 height=%2250%22 patternUnits=%22userSpaceOnUse%22%3E%3Cpath d=%22M0 0h50v50H0z%22 fill=%22%230f172a%22/%3E%3Cpath d=%22M25 0c13.807 0 25 11.193 25 25s-11.193 25-25 25S0 38.807 0 25 11.193 0 25 0z%22 fill=%22%23172554%22 fill-opacity=%220.4%22/%3E%3Cpath d=%22M12.5 12.5c6.904 0 12.5 5.596 12.5 12.5s-5.596 12.5-12.5 12.5S0 31.904 0 25s5.596-12.5 12.5-12.5z%22 fill=%22%231e293b%22 fill-opacity=%220.6%22/%3E%3Cpath d=%22M37.5 37.5c6.904 0 12.5 5.596 12.5 12.5s-5.596 12.5-12.5 12.5S25 56.904 25 50s5.596-12.5 12.5-12.5z%22 fill=%22%231e293b%22 fill-opacity=%220.6%22/%3E%3Cpath d=%22M6 6l4 4-4 4-4-4z%22 fill=%22%23334155%22 fill-opacity=%220.3%22/%3E%3Cpath d=%22M44 44l4 4-4 4-4-4z%22 fill=%22%23334155%22 fill-opacity=%220.3%22/%3E%3Cpath d=%22M19 6l4 4-4 4-4-4z%22 fill=%22%23334155%22 fill-opacity=%220.2%22/%3E%3Cpath d=%22M31 44l4 4-4 4-4-4z%22 fill=%22%23334155%22 fill-opacity=%220.2%22/%3E%3C/pattern%3E%3C/defs%3E%3Crect width=%22100%25%22 height=%22100%25%22 fill=%22url(%23darkTexture)%22/%3E%3C/svg%3E')] opacity-80"></div>
      <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width=%22100%22 height=%22100%22 viewBox=%220 0 100 100%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cdefs%3E%3Cpattern id=%22darkTexture%22 x=%220%22 y=%220%22 width=%2250%22 height=%2250%22 patternUnits=%22userSpaceOnUse%22%3E%3Cpath d=%22M0 0h50v50H0z%22 fill=%22%231a012b%22/%3E%3Cpath d=%22M25 0c13.807 0 25 11.193 25 25s-11.193 25-25 25S0 38.807 0 25 11.193 0 25 0z%22 fill=%22%23240135%22 fill-opacity=%220.4%22/%3E%3Cpath d=%22M12.5 12.5c6.904 0 12.5 5.596 12.5 12.5s-5.596 12.5-12.5 12.5S0 31.904 0 25s5.596-12.5 12.5-12.5z%22 fill=%22%232d0140%22 fill-opacity=%220.6%22/%3E%3Cpath d=%22M37.5 37.5c6.904 0 12.5 5.596 12.5 12.5s-5.596 12.5-12.5 12.5S25 56.904 25 50s5.596-12.5 12.5-12.5z%22 fill=%22%232d0140%22 fill-opacity=%220.6%22/%3E%3Cpath d=%22M6 6l4 4-4 4-4-4z%22 fill=%22%23380150%22 fill-opacity=%220.3%22/%3E%3Cpath d=%22M44 44l4 4-4 4-4-4z%22 fill=%22%23380150%22 fill-opacity=%220.3%22/%3E%3Cpath d=%22M19 6l4 4-4 4-4-4z%22 fill=%22%23380150%22 fill-opacity=%220.2%22/%3E%3Cpath d=%22M31 44l4 4-4 4-4-4z%22 fill=%22%23380150%22 fill-opacity=%220.2%22/%3E%3C/pattern%3E%3C/defs%3E%3Crect width=%22100%25%22 height=%22100%25%22 fill=%22url(%23darkTexture)%22/%3E%3C/svg%3E')] opacity-80"></div>
      <div className="absolute inset-0 bg-gradient-to-br from-purple-950/30 via-purple-900/20 to-purple-950/30"></div>

      <div className="relative z-10 flex h-screen">
        {/* Sidebar */}
        <div className="w-80 bg-white/95 backdrop-blur-sm shadow-2xl border-r border-purple-200/20">
          {/* Header */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 rounded-full flex items-center justify-center shadow-lg" style={{background: 'linear-gradient(to right, #b17a50, #c8855c)'}}>
                <Scissors className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Slotifyme LLC</h1>
                <p className="text-gray-600 text-sm">Management Dashboard</p>
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="p-4 space-y-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as 'plans' | 'tenants')}
                  className={`w-full text-left p-4 rounded-xl transition-all duration-200 ${
                    activeTab === tab.id
                      ? 'text-white shadow-lg transform scale-105'
                      : 'bg-gray-50 text-gray-700 hover:bg-gray-100 hover:transform hover:scale-102'
                  }`}
                  style={activeTab === tab.id ? {background: 'linear-gradient(to right, #b17a50, #c8855c)'} : {}}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className="w-5 h-5" />
                    <div>
                      <div className="font-semibold">{tab.label}</div>
                      <div className={`text-sm ${activeTab === tab.id ? 'text-orange-100' : 'text-gray-500'}`}>
                        {tab.description}
                      </div>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>

          {/* User Profile & Logout */}
          <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-white/95">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
               <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{background: 'linear-gradient(to right, #b17a50, #c8855c)'}}>
                  <User className="w-4 h-4 text-white" />
                </div>
                <div>
                  <div className="font-semibold text-gray-900 text-sm">Shop Owner</div>
                  <div className="text-gray-500 text-xs">owner@barbershop.com</div>
                </div>
              </div>
              <button className="text-gray-400 hover:text-gray-600 transition-colors">
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-auto">
          <div className="p-8">
            <div className="max-w-7xl mx-auto">
              {activeTab === 'plans' ? renderPlansContent() : renderTenantsContent()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;