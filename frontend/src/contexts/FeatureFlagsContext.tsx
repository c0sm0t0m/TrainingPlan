import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

/**
 * Feature Flags Configuration
 * 
 * Controls experimental features. Use for A/B testing and safe rollout of new features.
 * Add new flags here as needed for experimental features.
 */
export interface FeatureFlags {
  // Visual improvements
  newColorTheme: boolean;
}

interface FeatureFlagsContextValue {
  features: FeatureFlags;
  toggleFeature: (key: keyof FeatureFlags) => void;
  resetFeatures: () => void;
  enableAll: () => void;
  disableAll: () => void;
}

// Default feature flags (safe defaults for production)
const DEFAULT_FEATURES: FeatureFlags = {
  newColorTheme: false, // Modern athletic color palette
};

// Environment variable overrides (VITE_FEATURE_*)
const getEnvOverrides = (): Partial<FeatureFlags> => {
  const overrides: Partial<FeatureFlags> = {};
  
  Object.keys(DEFAULT_FEATURES).forEach((key) => {
    const envKey = `VITE_FEATURE_${key.replace(/([A-Z])/g, '_$1').toUpperCase()}`;
    const envValue = import.meta.env[envKey];
    
    if (envValue !== undefined) {
      overrides[key as keyof FeatureFlags] = envValue === 'true' || envValue === '1';
    }
  });
  
  return overrides;
};

// URL parameter overrides (?newNavigation=true)
const getUrlOverrides = (): Partial<FeatureFlags> => {
  const overrides: Partial<FeatureFlags> = {};
  const params = new URLSearchParams(window.location.search);
  
  Object.keys(DEFAULT_FEATURES).forEach((key) => {
    const paramValue = params.get(key);
    if (paramValue !== null) {
      overrides[key as keyof FeatureFlags] = paramValue === 'true' || paramValue === '1';
    }
  });
  
  return overrides;
};

// localStorage overrides (persistent user preference)
const getLocalStorageOverrides = (): Partial<FeatureFlags> => {
  const overrides: Partial<FeatureFlags> = {};
  
  Object.keys(DEFAULT_FEATURES).forEach((key) => {
    const storageKey = `feature_${key}`;
    const storedValue = localStorage.getItem(storageKey);
    
    if (storedValue !== null) {
      overrides[key as keyof FeatureFlags] = storedValue === 'true';
    }
  });
  
  return overrides;
};

// Save to localStorage
const saveToLocalStorage = (features: FeatureFlags) => {
  Object.entries(features).forEach(([key, value]) => {
    localStorage.setItem(`feature_${key}`, String(value));
  });
};

// Merge all sources (priority: URL > localStorage > env > defaults)
const getInitialFeatures = (): FeatureFlags => {
  return {
    ...DEFAULT_FEATURES,
    ...getEnvOverrides(),
    ...getLocalStorageOverrides(),
    ...getUrlOverrides(), // URL has highest priority
  };
};

const FeatureFlagsContext = createContext<FeatureFlagsContextValue | undefined>(undefined);

interface FeatureFlagsProviderProps {
  children: ReactNode;
}

export const FeatureFlagsProvider: React.FC<FeatureFlagsProviderProps> = ({ children }) => {
  const [features, setFeatures] = useState<FeatureFlags>(getInitialFeatures);

  // Save to localStorage whenever features change
  useEffect(() => {
    saveToLocalStorage(features);
  }, [features]);

  // Log active features in development
  useEffect(() => {
    if (import.meta.env.DEV) {
      const activeFeatures = Object.entries(features)
        .filter(([_, enabled]) => enabled)
        .map(([key]) => key);
      
      if (activeFeatures.length > 0) {
        console.log('🚩 Active Feature Flags:', activeFeatures);
      }
    }
  }, [features]);

  const toggleFeature = (key: keyof FeatureFlags) => {
    setFeatures((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const resetFeatures = () => {
    setFeatures(DEFAULT_FEATURES);
    // Clear localStorage
    Object.keys(DEFAULT_FEATURES).forEach((key) => {
      localStorage.removeItem(`feature_${key}`);
    });
  };

  const enableAll = () => {
    const allEnabled = Object.keys(DEFAULT_FEATURES).reduce(
      (acc, key) => ({ ...acc, [key]: true }),
      {} as FeatureFlags
    );
    setFeatures(allEnabled);
  };

  const disableAll = () => {
    setFeatures(DEFAULT_FEATURES);
  };

  return (
    <FeatureFlagsContext.Provider
      value={{
        features,
        toggleFeature,
        resetFeatures,
        enableAll,
        disableAll,
      }}
    >
      {children}
    </FeatureFlagsContext.Provider>
  );
};

export const useFeatureFlags = (): FeatureFlagsContextValue => {
  const context = useContext(FeatureFlagsContext);
  if (!context) {
    throw new Error('useFeatureFlags must be used within a FeatureFlagsProvider');
  }
  return context;
};

// Convenience hook for checking a single feature
export const useFeature = (key: keyof FeatureFlags): boolean => {
  const { features } = useFeatureFlags();
  return features[key];
};

// Export for type checking
export default FeatureFlagsContext;
