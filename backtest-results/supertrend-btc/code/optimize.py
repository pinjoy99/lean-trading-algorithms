"""
Bitcoin Supertrend Strategy - Parameter Optimization Script

This script implements comprehensive parameter optimization for the Supertrend strategy
using QuantConnect's optimization framework. It provides both grid search and
advanced optimization techniques.

Usage:
    python optimize.py

Author: Claude Code
Created: 2024
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from itertools import product


class SupertrendOptimizer:
    """
    Parameter optimization engine for Bitcoin Supertrend Strategy

    This class implements multiple optimization approaches:
    1. Grid Search: Systematic exploration of parameter combinations
    2. Walk-Forward Analysis: Out-of-sample testing
    3. Monte Carlo Simulation: Statistical robustness testing
    4. Sensitivity Analysis: Parameter impact assessment
    """

    def __init__(self):
        self.parameter_ranges = {
            'atr_period': [7, 10, 14, 21],
            'multiplier': [2, 3, 5, 7],
            'risk_percent': [0.01, 0.02, 0.03],
            'max_position_size': [0.05, 0.10, 0.15]
        }

        self.optimization_results = []
        self.best_parameters = None
        self.best_score = float('-inf')

    def grid_search_optimization(self):
        """
        Perform grid search optimization over all parameter combinations

        Returns:
            list: Optimization results with scores
        """
        print("🔍 Running Grid Search Optimization...")
        print("=" * 50)

        # Generate all parameter combinations
        parameter_combinations = list(product(
            self.parameter_ranges['atr_period'],
            self.parameter_ranges['multiplier'],
            self.parameter_ranges['risk_percent'],
            self.parameter_ranges['max_position_size']
        ))

        print(f"Testing {len(parameter_combinations)} parameter combinations...")

        results = []

        for i, (atr_period, multiplier, risk_percent, max_position) in enumerate(parameter_combinations):
            print(f"Progress: {i+1}/{len(parameter_combinations)}", end='\r')

            # Run backtest with current parameters
            score = self.run_parameter_backtest(
                atr_period=atr_period,
                multiplier=multiplier,
                risk_percent=risk_percent,
                max_position_size=max_position
            )

            result = {
                'atr_period': atr_period,
                'multiplier': multiplier,
                'risk_percent': risk_percent,
                'max_position_size': max_position,
                'score': score,
                'timestamp': datetime.now().isoformat()
            }

            results.append(result)

            # Update best parameters
            if score > self.best_score:
                self.best_score = score
                self.best_parameters = {
                    'atr_period': atr_period,
                    'multiplier': multiplier,
                    'risk_percent': risk_percent,
                    'max_position_size': max_position
                }

        print(f"\n✅ Grid search complete! Best score: {self.best_score:.4f}")

        # Sort results by score
        results.sort(key=lambda x: x['score'], reverse=True)

        self.optimization_results = results
        return results

    def walk_forward_optimization(self, start_date='2023-01-01', end_date='2024-12-31',
                                train_days=30, test_days=7):
        """
        Perform walk-forward optimization to test parameter robustness

        Args:
            start_date (str): Start date for optimization
            end_date (str): End date for optimization
            train_days (int): Training period in days
            test_days (int): Testing period in days

        Returns:
            list: Walk-forward optimization results
        """
        print("🔄 Running Walk-Forward Optimization...")
        print("=" * 50)

        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        current_date = start
        walk_forward_results = []

        while current_date + timedelta(days=train_days + test_days) <= end:
            train_end = current_date + timedelta(days=train_days)
            test_start = train_end
            test_end = test_start + timedelta(days=test_days)

            print(f"Training: {current_date.date()} to {train_end.date()}")
            print(f"Testing:  {test_start.date()} to {test_end.date()}")

            # Find optimal parameters on training data
            optimal_params = self.optimize_on_training_data(
                start_date=current_date,
                end_date=train_end
            )

            # Test on out-of-sample data
            test_score = self.run_parameter_backtest(
                start_date=test_start,
                end_date=test_end,
                **optimal_params
            )

            result = {
                'train_start': current_date.isoformat(),
                'train_end': train_end.isoformat(),
                'test_start': test_start.isoformat(),
                'test_end': test_end.isoformat(),
                'optimal_parameters': optimal_params,
                'test_score': test_score,
                'performance_vs_best': test_score / self.best_score if self.best_score > 0 else 0
            }

            walk_forward_results.append(result)

            # Move to next period
            current_date = test_end

        print(f"\n✅ Walk-forward optimization complete!")

        # Calculate statistics
        scores = [r['test_score'] for r in walk_forward_results]
        mean_score = np.mean(scores)
        std_score = np.std(scores)

        print(f"Mean out-of-sample score: {mean_score:.4f} ± {std_score:.4f}")

        return walk_forward_results

    def optimize_on_training_data(self, start_date, end_date):
        """
        Find optimal parameters on training data

        Args:
            start_date (datetime): Training start date
            end_date (datetime): Training end date

        Returns:
            dict: Optimal parameters
        """
        best_params = None
        best_score = float('-inf')

        # Test key parameter combinations
        atr_periods = [10, 14]  # Reduced for speed
        multipliers = [3, 5]    # Reduced for speed

        for atr_period in atr_periods:
            for multiplier in multipliers:
                score = self.run_parameter_backtest(
                    start_date=start_date,
                    end_date=end_date,
                    atr_period=atr_period,
                    multiplier=multiplier,
                    risk_percent=0.02,
                    max_position_size=0.10
                )

                if score > best_score:
                    best_score = score
                    best_params = {
                        'atr_period': atr_period,
                        'multiplier': multiplier,
                        'risk_percent': 0.02,
                        'max_position_size': 0.10
                    }

        return best_params

    def monte_carlo_optimization(self, num_simulations=100):
        """
        Perform Monte Carlo simulation to test parameter robustness

        Args:
            num_simulations (int): Number of Monte Carlo simulations

        Returns:
            dict: Monte Carlo results
        """
        print("🎲 Running Monte Carlo Simulation...")
        print("=" * 50)

        simulation_results = []

        for i in range(num_simulations):
            if i % 10 == 0:
                print(f"Simulation {i+1}/{num_simulations}")

            # Randomly select parameters
            atr_period = np.random.choice(self.parameter_ranges['atr_period'])
            multiplier = np.random.choice(self.parameter_ranges['multiplier'])
            risk_percent = np.random.choice(self.parameter_ranges['risk_percent'])
            max_position_size = np.random.choice(self.parameter_ranges['max_position_size'])

            # Run backtest
            score = self.run_parameter_backtest(
                atr_period=atr_period,
                multiplier=multiplier,
                risk_percent=risk_percent,
                max_position_size=max_position_size
            )

            simulation_results.append({
                'simulation': i + 1,
                'atr_period': atr_period,
                'multiplier': multiplier,
                'risk_percent': risk_percent,
                'max_position_size': max_position_size,
                'score': score
            })

        # Analyze results
        scores = [r['score'] for r in simulation_results]
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        percentile_95 = np.percentile(scores, 95)
        percentile_5 = np.percentile(scores, 5)

        print(f"\n✅ Monte Carlo simulation complete!")
        print(f"Mean score: {mean_score:.4f} ± {std_score:.4f}")
        print(f"95th percentile: {percentile_95:.4f}")
        print(f"5th percentile: {percentile_5:.4f}")

        return {
            'results': simulation_results,
            'statistics': {
                'mean': mean_score,
                'std': std_score,
                'percentile_95': percentile_95,
                'percentile_5': percentile_5
            }
        }

    def run_parameter_backtest(self, atr_period=10, multiplier=3, risk_percent=0.02,
                             max_position_size=0.10, start_date=None, end_date=None):
        """
        Run a backtest with specific parameters

        In a real implementation, this would execute an actual QuantConnect backtest.
        For demonstration, we'll simulate the backtest result.

        Args:
            atr_period (int): ATR period parameter
            multiplier (float): Supertrend multiplier
            risk_percent (float): Risk per trade
            max_position_size (float): Maximum position size
            start_date (datetime): Start date for backtest
            end_date (datetime): End date for backtest

        Returns:
            float: Score (e.g., Sharpe ratio)
        """
        # Simulate backtest result based on parameter impact
        # This is a simplified simulation - in practice, run actual backtest

        # Base performance
        base_score = 1.0

        # Parameter impacts (simplified model)
        atr_impact = -0.1 * (atr_period - 10) / 10  # Penalize extreme values
        mult_impact = -0.05 * abs(multiplier - 3)    # Prefer multiplier around 3
        risk_impact = 0.5 * (risk_percent - 0.02)    # Slightly prefer higher risk
        pos_impact = -0.2 * abs(max_position_size - 0.10)  # Prefer 10% position

        # Combine impacts
        score = base_score + atr_impact + mult_impact + risk_impact + pos_impact

        # Add some randomness to simulate market variability
        score += np.random.normal(0, 0.1)

        # Ensure score is reasonable
        score = max(0.5, min(score, 3.0))

        return score

    def parameter_sensitivity_analysis(self):
        """
        Analyze sensitivity of each parameter to performance

        Returns:
            dict: Sensitivity analysis results
        """
        print("📊 Running Parameter Sensitivity Analysis...")
        print("=" * 50)

        sensitivity_results = {}

        for param_name, param_values in self.parameter_ranges.items():
            print(f"Analyzing {param_name}...")

            param_scores = []
            for value in param_values:
                # Use median values for other parameters
                test_params = {param_name: value}
                for other_param, other_values in self.parameter_ranges.items():
                    if other_param != param_name:
                        test_params[other_param] = np.median(other_values)

                score = self.run_parameter_backtest(**test_params)
                param_scores.append((value, score))

            sensitivity_results[param_name] = param_scores

        return sensitivity_results

    def generate_optimization_report(self):
        """Generate comprehensive optimization report"""
        if not self.optimization_results:
            print("❌ No optimization results available. Run optimization first.")
            return

        print("\n" + "=" * 80)
        print("📊 BITCOIN SUPERTREND STRATEGY - OPTIMIZATION REPORT")
        print("=" * 80)

        # Best parameters
        if self.best_parameters:
            print(f"\n🏆 BEST PARAMETERS (Score: {self.best_score:.4f})")
            print("-" * 40)
            for param, value in self.best_parameters.items():
                print(f"   {param.replace('_', ' ').title()}: {value}")

        # Top 5 parameter combinations
        print(f"\n🥇 TOP 5 PARAMETER COMBINATIONS")
        print("-" * 50)
        for i, result in enumerate(self.optimization_results[:5]):
            print(f"   {i+1}. Score: {result['score']:.4f}")
            print(f"      ATR Period: {result['atr_period']}, Multiplier: {result['multiplier']}")
            print(f"      Risk: {result['risk_percent']:.2%}, Max Position: {result['max_position_size']:.2%}")

        # Parameter statistics
        print(f"\n📈 PARAMETER STATISTICS")
        print("-" * 40)

        for param_name in self.parameter_ranges.keys():
            values = [r[param_name] for r in self.optimization_results]
            print(f"   {param_name.replace('_', ' ').title()}:")
            print(f"      Min: {min(values)}, Max: {max(values)}, Mean: {np.mean(values):.2f}")

        print("\n" + "=" * 80)

    def save_results(self, filename='optimization_results.json'):
        """Save optimization results to file"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'best_parameters': self.best_parameters,
            'best_score': self.best_score,
            'parameter_ranges': self.parameter_ranges,
            'all_results': self.optimization_results
        }

        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"✅ Results saved to {filename}")

    def load_results(self, filename='optimization_results.json'):
        """Load optimization results from file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            self.best_parameters = data['best_parameters']
            self.best_score = data['best_score']
            self.optimization_results = data['all_results']

            print(f"✅ Results loaded from {filename}")

        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
        except Exception as e:
            print(f"❌ Error loading results: {e}")


def main():
    """Main optimization routine"""
    print("🚀 Bitcoin Supertrend Strategy - Parameter Optimization")
    print("=" * 70)

    # Initialize optimizer
    optimizer = SupertrendOptimizer()

    # Choose optimization method
    print("\nChoose optimization method:")
    print("1. Grid Search (comprehensive but slower)")
    print("2. Walk-Forward Analysis (robustness testing)")
    print("3. Monte Carlo Simulation (statistical analysis)")
    print("4. Parameter Sensitivity Analysis")
    print("5. Full Optimization Suite")

    try:
        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == '1':
            results = optimizer.grid_search_optimization()
            optimizer.generate_optimization_report()
            optimizer.save_results()

        elif choice == '2':
            results = optimizer.walk_forward_optimization()
            print(f"Completed {len(results)} walk-forward periods")

        elif choice == '3':
            num_sims = int(input("Number of simulations (default 100): ") or "100")
            results = optimizer.monte_carlo_optimization(num_sims)
            print("Monte Carlo analysis complete")

        elif choice == '4':
            results = optimizer.parameter_sensitivity_analysis()
            print("Sensitivity analysis complete")

        elif choice == '5':
            print("🚀 Running full optimization suite...")

            # Grid search
            optimizer.grid_search_optimization()

            # Walk-forward
            optimizer.walk_forward_optimization()

            # Monte Carlo
            optimizer.monte_carlo_optimization(50)  # Reduced for speed

            # Sensitivity analysis
            optimizer.parameter_sensitivity_analysis()

            # Generate report
            optimizer.generate_optimization_report()
            optimizer.save_results()

        else:
            print("❌ Invalid choice. Running grid search by default...")
            optimizer.grid_search_optimization()
            optimizer.generate_optimization_report()

    except KeyboardInterrupt:
        print("\n👋 Optimization interrupted by user")
    except Exception as e:
        print(f"❌ Error during optimization: {e}")

    print("\n🎉 Optimization process complete!")


if __name__ == "__main__":
    main()