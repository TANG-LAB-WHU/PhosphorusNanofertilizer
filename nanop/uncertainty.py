"""
Uncertainty Analysis Module

Provides Monte Carlo simulation and sensitivity analysis functionality.
"""

import numpy as np
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class UncertaintyResult:
    """Results from uncertainty analysis."""
    
    metric_name: str
    mean: float
    std: float
    percentiles: Dict[int, float] = field(default_factory=dict)
    samples: np.ndarray = field(default_factory=lambda: np.array([]))
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    
    def __post_init__(self):
        if len(self.samples) > 0 and not self.percentiles:
            self.percentiles = {
                5: np.percentile(self.samples, 5),
                25: np.percentile(self.samples, 25),
                50: np.percentile(self.samples, 50),
                75: np.percentile(self.samples, 75),
                95: np.percentile(self.samples, 95),
            }
            self.confidence_interval = (self.percentiles[5], self.percentiles[95])


@dataclass
class SensitivityResult:
    """Results from sensitivity analysis."""
    
    parameter: str
    base_value: float
    sensitivity_ratio: float  # % change in output / % change in input
    elasticity: float  # Normalized sensitivity
    tornado_values: Tuple[float, float] = (0.0, 0.0)  # (low, high) output values


class UncertaintyEngine:
    """
    Uncertainty analysis engine for LCA-TEA.
    
    Provides:
    - Monte Carlo simulation
    - Sensitivity analysis (OAT)
    - Parameter sampling from distributions
    """
    
    DISTRIBUTION_TYPES = ["normal", "uniform", "triangular", "lognormal"]
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize uncertainty engine.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.rng = np.random.default_rng(seed)
    
    def sample_parameter(
        self,
        distribution: Dict,
        n_samples: int = 1000
    ) -> np.ndarray:
        """
        Sample from a parameter distribution.
        
        Args:
            distribution: Dict with 'type' and distribution parameters
            n_samples: Number of samples
            
        Returns:
            Array of sampled values
        """
        dist_type = distribution.get("type", "normal")
        
        if dist_type == "normal":
            mean = distribution.get("mean", distribution.get("mode", 0))
            std = distribution.get("std", mean * 0.1)
            return self.rng.normal(mean, std, n_samples)
        
        elif dist_type == "uniform":
            low = distribution.get("min", 0)
            high = distribution.get("max", 1)
            return self.rng.uniform(low, high, n_samples)
        
        elif dist_type == "triangular":
            left = distribution.get("min", 0)
            mode = distribution.get("mode", 0.5)
            right = distribution.get("max", 1)
            return self.rng.triangular(left, mode, right, n_samples)
        
        elif dist_type == "lognormal":
            mean = distribution.get("mean", 1)
            sigma = distribution.get("sigma", 0.5)
            return self.rng.lognormal(np.log(mean), sigma, n_samples)
        
        else:
            raise ValueError(f"Unknown distribution type: {dist_type}")
    
    def monte_carlo(
        self,
        model_func: Callable,
        parameter_distributions: Dict[str, Dict],
        n_iterations: int = 1000,
        base_params: Optional[Dict] = None
    ) -> Dict[str, UncertaintyResult]:
        """
        Run Monte Carlo simulation.
        
        Args:
            model_func: Function that takes parameters and returns results dict
            parameter_distributions: Dict mapping param names to distributions
            n_iterations: Number of Monte Carlo iterations
            base_params: Base parameter values (non-uncertain)
            
        Returns:
            Dict mapping output names to UncertaintyResult
        """
        base_params = base_params or {}
        
        # Sample all parameters
        sampled_params = {}
        for param, dist in parameter_distributions.items():
            sampled_params[param] = self.sample_parameter(dist, n_iterations)
        
        # Run model for each iteration
        results_list = []
        for i in range(n_iterations):
            params = base_params.copy()
            for param, samples in sampled_params.items():
                params[param] = samples[i]
            
            try:
                result = model_func(params)
                results_list.append(result)
            except Exception:
                continue
        
        if not results_list:
            return {}
        
        # Aggregate results for each output
        output_keys = results_list[0].keys()
        uncertainty_results = {}
        
        for key in output_keys:
            values = np.array([r[key] for r in results_list if key in r])
            if len(values) > 0:
                uncertainty_results[key] = UncertaintyResult(
                    metric_name=key,
                    mean=np.mean(values),
                    std=np.std(values),
                    samples=values
                )
        
        return uncertainty_results
    
    def sensitivity_analysis(
        self,
        model_func: Callable,
        base_params: Dict,
        parameters_to_vary: List[str],
        variation_pct: float = 0.1
    ) -> List[SensitivityResult]:
        """
        One-at-a-time sensitivity analysis.
        
        Args:
            model_func: Function that takes parameters and returns single value
            base_params: Base parameter values
            parameters_to_vary: List of parameter names to analyze
            variation_pct: Percentage to vary each parameter (±)
            
        Returns:
            List of SensitivityResult for each parameter
        """
        # Calculate base case
        base_result = model_func(base_params)
        if isinstance(base_result, dict):
            base_value = list(base_result.values())[0]
        else:
            base_value = base_result
        
        results = []
        
        for param in parameters_to_vary:
            if param not in base_params:
                continue
            
            param_base = base_params[param]
            
            # Low case
            low_params = base_params.copy()
            low_params[param] = param_base * (1 - variation_pct)
            low_result = model_func(low_params)
            if isinstance(low_result, dict):
                low_value = list(low_result.values())[0]
            else:
                low_value = low_result
            
            # High case
            high_params = base_params.copy()
            high_params[param] = param_base * (1 + variation_pct)
            high_result = model_func(high_params)
            if isinstance(high_result, dict):
                high_value = list(high_result.values())[0]
            else:
                high_value = high_result
            
            # Calculate sensitivity
            delta_output = high_value - low_value
            delta_input = 2 * variation_pct * param_base
            
            if param_base != 0 and base_value != 0:
                sensitivity = (delta_output / base_value) / (delta_input / param_base)
            else:
                sensitivity = 0
            
            results.append(SensitivityResult(
                parameter=param,
                base_value=param_base,
                sensitivity_ratio=sensitivity,
                elasticity=abs(sensitivity),
                tornado_values=(low_value, high_value)
            ))
        
        # Sort by elasticity (most sensitive first)
        results.sort(key=lambda x: x.elasticity, reverse=True)
        
        return results
    
    def tornado_data(
        self,
        sensitivity_results: List[SensitivityResult],
        base_value: float
    ) -> Dict:
        """
        Prepare data for tornado diagram.
        
        Args:
            sensitivity_results: Results from sensitivity analysis
            base_value: Base case value
            
        Returns:
            Dict with tornado plot data
        """
        return {
            "parameters": [r.parameter for r in sensitivity_results],
            "low_values": [r.tornado_values[0] for r in sensitivity_results],
            "high_values": [r.tornado_values[1] for r in sensitivity_results],
            "base_value": base_value,
            "elasticities": [r.elasticity for r in sensitivity_results]
        }


if __name__ == "__main__":
    # Example usage
    engine = UncertaintyEngine(seed=42)
    
    # Sample from triangular distribution
    samples = engine.sample_parameter({
        "type": "triangular",
        "min": 0.8,
        "mode": 1.0,
        "max": 1.2
    }, 1000)
    
    print(f"Mean: {np.mean(samples):.3f}")
    print(f"Std: {np.std(samples):.3f}")
