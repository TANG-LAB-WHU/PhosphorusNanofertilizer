"""
ML Gap-Filling Module

Machine learning methods for filling missing LCA-TEA data.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


@dataclass
class GapFillingResult:
    """Result from gap-filling prediction."""
    
    parameter: str
    predicted_value: float
    confidence: float
    method: str
    uncertainty: float = 0.0
    similar_cases: List[Dict] = None
    
    def __post_init__(self):
        if self.similar_cases is None:
            self.similar_cases = []


class SimilarityMatcher:
    """
    Find similar processes/materials based on properties.
    """
    
    def __init__(self):
        self.database: List[Dict] = []
    
    def add_reference(self, item: Dict) -> None:
        """Add a reference item to the database."""
        self.database.append(item)
    
    def find_similar(
        self,
        query: Dict,
        feature_keys: List[str],
        top_k: int = 5
    ) -> List[Tuple[Dict, float]]:
        """
        Find similar items based on feature similarity.
        
        Args:
            query: Query item with properties
            feature_keys: Keys to use for comparison
            top_k: Number of results
            
        Returns:
            List of (item, similarity_score) tuples
        """
        if not self.database:
            return []
        
        scores = []
        query_vec = self._to_vector(query, feature_keys)
        
        for item in self.database:
            item_vec = self._to_vector(item, feature_keys)
            sim = self._cosine_similarity(query_vec, item_vec)
            scores.append((item, sim))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
    def _to_vector(self, item: Dict, keys: List[str]) -> np.ndarray:
        """Convert item to feature vector."""
        values = []
        for key in keys:
            val = item.get(key, 0)
            if isinstance(val, (int, float)):
                values.append(float(val))
            else:
                values.append(0.0)
        return np.array(values)
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity."""
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot / (norm_a * norm_b)


class RegressionPredictor:
    """
    Simple regression for predicting missing values.
    """
    
    def __init__(self):
        self.models: Dict[str, Tuple] = {}  # parameter -> (coeffs, intercept)
        self.training_data: List[Dict] = []
    
    def add_training_data(self, data: List[Dict]) -> None:
        """Add training data."""
        self.training_data.extend(data)
    
    def train(
        self,
        target: str,
        features: List[str]
    ) -> bool:
        """
        Train a simple linear regression model.
        
        Args:
            target: Target parameter to predict
            features: Feature parameters
            
        Returns:
            Whether training was successful
        """
        if len(self.training_data) < 3:
            return False
        
        # Extract data
        X = []
        y = []
        
        for item in self.training_data:
            if target not in item:
                continue
            
            row = []
            valid = True
            for f in features:
                if f in item and isinstance(item[f], (int, float)):
                    row.append(float(item[f]))
                else:
                    valid = False
                    break
            
            if valid:
                X.append(row)
                y.append(float(item[target]))
        
        if len(X) < 3:
            return False
        
        X = np.array(X)
        y = np.array(y)
        
        # Simple least squares (with bias term)
        X_bias = np.column_stack([np.ones(len(X)), X])
        
        try:
            coeffs = np.linalg.lstsq(X_bias, y, rcond=None)[0]
            self.models[target] = (coeffs[1:], coeffs[0])
            return True
        except:
            return False
    
    def predict(
        self,
        target: str,
        features: Dict[str, float]
    ) -> Optional[float]:
        """Predict a target value from features."""
        if target not in self.models:
            return None
        
        coeffs, intercept = self.models[target]
        
        # Build feature vector in correct order
        x = np.array([features.get(f, 0) for f in range(len(coeffs))])
        
        return float(np.dot(coeffs, x) + intercept)


class GapFiller:
    """
    Gap-filling engine for missing LCA-TEA data.
    
    Methods:
    1. Similarity matching - find similar processes
    2. Regression prediction - predict from relationships
    3. Default values with uncertainty
    """
    
    # Default values for common parameters (with uncertainty %)
    DEFAULT_VALUES = {
        "electricity_kwh": (500, 0.3),  # kWh/tonne, 30% uncertainty
        "water_kg": (5000, 0.4),
        "thermal_energy_kwh": (800, 0.3),
        "co2_emission_factor": (0.475, 0.2),  # kg CO2/kWh
        "yield_pct": (0.9, 0.1),
    }
    
    def __init__(self):
        self.similarity_matcher = SimilarityMatcher()
        self.regression = RegressionPredictor()
    
    def add_reference_data(self, data: List[Dict]) -> None:
        """Add reference data for similarity and regression."""
        for item in data:
            self.similarity_matcher.add_reference(item)
        self.regression.add_training_data(data)
    
    def fill_gap(
        self,
        parameter: str,
        context: Dict,
        method: str = "auto"
    ) -> GapFillingResult:
        """
        Fill a missing parameter value.
        
        Args:
            parameter: Parameter name to fill
            context: Context with known values
            method: 'similarity', 'regression', 'default', or 'auto'
            
        Returns:
            GapFillingResult
        """
        if method == "auto":
            # Try methods in order of preference
            result = self._try_similarity(parameter, context)
            if result and result.confidence > 0.7:
                return result
            
            result = self._try_regression(parameter, context)
            if result:
                return result
            
            return self._use_default(parameter)
        
        elif method == "similarity":
            return self._try_similarity(parameter, context) or self._use_default(parameter)
        
        elif method == "regression":
            return self._try_regression(parameter, context) or self._use_default(parameter)
        
        else:
            return self._use_default(parameter)
    
    def _try_similarity(
        self,
        parameter: str,
        context: Dict
    ) -> Optional[GapFillingResult]:
        """Try similarity-based gap filling."""
        feature_keys = list(context.keys())
        similar = self.similarity_matcher.find_similar(context, feature_keys, top_k=3)
        
        if not similar:
            return None
        
        # Extract parameter values from similar items
        values = []
        for item, score in similar:
            if parameter in item:
                values.append((item[parameter], score))
        
        if not values:
            return None
        
        # Weighted average
        total_weight = sum(s for _, s in values)
        if total_weight == 0:
            return None
        
        weighted_value = sum(v * s for v, s in values) / total_weight
        avg_confidence = total_weight / len(similar)
        
        return GapFillingResult(
            parameter=parameter,
            predicted_value=weighted_value,
            confidence=avg_confidence,
            method="similarity",
            uncertainty=0.2,  # 20% uncertainty
            similar_cases=[{"value": v, "score": s} for v, s in values[:3]]
        )
    
    def _try_regression(
        self,
        parameter: str,
        context: Dict
    ) -> Optional[GapFillingResult]:
        """Try regression-based gap filling."""
        features = list(context.keys())
        
        if not self.regression.train(parameter, features):
            return None
        
        predicted = self.regression.predict(parameter, context)
        
        if predicted is None:
            return None
        
        return GapFillingResult(
            parameter=parameter,
            predicted_value=predicted,
            confidence=0.6,
            method="regression",
            uncertainty=0.25
        )
    
    def _use_default(self, parameter: str) -> GapFillingResult:
        """Use default value."""
        if parameter in self.DEFAULT_VALUES:
            value, uncertainty = self.DEFAULT_VALUES[parameter]
            return GapFillingResult(
                parameter=parameter,
                predicted_value=value,
                confidence=0.3,
                method="default",
                uncertainty=uncertainty
            )
        
        return GapFillingResult(
            parameter=parameter,
            predicted_value=0.0,
            confidence=0.0,
            method="unknown",
            uncertainty=1.0
        )


if __name__ == "__main__":
    # Example usage
    filler = GapFiller()
    
    # Add some reference data
    reference_data = [
        {"capacity": 10000, "electricity_kwh": 450, "water_kg": 8000},
        {"capacity": 5000, "electricity_kwh": 400, "water_kg": 6000},
        {"capacity": 20000, "electricity_kwh": 500, "water_kg": 10000},
    ]
    filler.add_reference_data(reference_data)
    
    # Fill a gap
    context = {"capacity": 15000}
    result = filler.fill_gap("electricity_kwh", context)
    
    print(f"Gap filling result:")
    print(f"  Parameter: {result.parameter}")
    print(f"  Predicted: {result.predicted_value:.1f}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Method: {result.method}")
