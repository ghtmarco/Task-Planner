import google.generativeai as genai
import os
import re
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleScheduler:
    def __init__(self):
        api_key = "YOUR_GEMINI_API_KEY_HERE"
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        self.rf_model = None
        self.scaler = None
        self.feature_names = None
        try:
            self.rf_model = joblib.load('Models/random_forest_model.pkl')
            self.scaler = joblib.load('Models/scaler.pkl')
            self.feature_names = joblib.load('Models/feature_names.pkl')
            logger.info("Successfully loaded ML models and feature names")
        except Exception as e:
            logger.warning(f"Failed to load ML models: {str(e)}")
            logger.warning("Will fall back to rule-based scheduling")

    def extract_features(self, goals, available_hours, considerations):
        features = {
            'available_hours': float(available_hours),
            'start_hour': max(6, 24 - available_hours),
        }
        features['end_hour'] = min(22, features['start_hour'] + available_hours)
        features['duration_blocks'] = available_hours / 2

        words = goals.lower().split()
        unique_words = set(words)
        features.update({
            'task_complexity': len(words) / 10,
            'task_diversity': len(unique_words) / len(words)
        })

        keyword_categories = {
            'is_creative': ['design', 'create', 'develop', 'build', 'implement'],
            'is_analytical': ['analyze', 'research', 'study', 'investigate', 'solve'],
            'is_planning': ['plan', 'organize', 'schedule', 'coordinate', 'arrange'],
            'prefers_morning': ['morning', 'early', 'am'],
            'prefers_afternoon': ['afternoon', 'lunch', 'pm'],
            'prefers_evening': ['evening', 'night', 'late'],
            'style_visual': ['visual', 'see', 'watch', 'look'],
            'style_auditory': ['listen', 'hear', 'discuss', 'talk'],
            'style_kinesthetic': ['practice', 'hands-on', 'do', 'experience']
        }

        considerations_lower = considerations.lower()
        
        features.update({
            feature_name: float(any(kw in unique_words or kw in considerations_lower for kw in keywords))
            for feature_name, keywords in keyword_categories.items()
        })

        deadline_words = ['deadline', 'due', 'urgent', 'asap', 'priority']
        features.update({
            'urgency_score': sum(word in considerations_lower for word in deadline_words) / len(deadline_words),
            'has_meetings': float('meeting' in considerations_lower),
            'has_breaks': float('break' in considerations_lower),
            'meeting_frequency': float(considerations_lower.count('meeting'))
        })
        
        features_df = pd.DataFrame([features])
        
        if self.feature_names is not None:
            try:
                features_df = features_df.reindex(columns=self.feature_names, fill_value=0)
                logger.info("Successfully aligned features with model expectations")
            except Exception as e:
                logger.error(f"Error aligning features: {str(e)}")
        
        if self.scaler:
            try:
                return self.scaler.transform(features_df)
            except Exception as e:
                logger.error(f"Error in scaling features: {str(e)}")
                return features_df.values
        
        return features_df.values

    def predict_optimal_slots(self, features):
        if self.rf_model is None:
            logger.warning("Random Forest model not available, using fallback scheduling")
            return None
            
        try:
            predictions = self.rf_model.predict_proba(features)
            if len(predictions) == 0:
                logger.error("No predictions generated by the model")
                return None
                
            hours = np.arange(24)
            hour_mask = (5 <= hours) & (hours <= 22)
            
            if predictions.shape[1] > 1:
                probs = predictions[:, 1]
            else:
                probs = predictions.flatten()
                
            probs = probs[hour_mask]
            valid_hours = hours[hour_mask]
            
            morning_boost = np.where((9 <= valid_hours) & (valid_hours <= 11), 1.2, 1.0)
            afternoon_boost = np.where((14 <= valid_hours) & (valid_hours <= 16), 1.1, 1.0)
            edge_penalty = np.where((valid_hours < 7) | (valid_hours > 20), 0.8, 1.0)
            
            adjustments = morning_boost * afternoon_boost * edge_penalty
            probs = probs * adjustments
            
            probs = np.clip(probs, 0, 1)
            slots = list(zip(valid_hours, probs))
            
            logger.info("Successfully generated optimal time slots")
            return sorted(slots, key=lambda x: x[1], reverse=True)
            
        except Exception as e:
            logger.error(f"Error in predicting optimal slots: {str(e)}")
            return None

    def generate_dynamic_schedule(self, duration, goals, available_hours, considerations):
        features = self.extract_features(goals, available_hours, considerations)
        optimal_slots = self.predict_optimal_slots(features)
        hours_needed = min(int(available_hours), 12)
        
        if optimal_slots is None:
            logger.info("Using rule-based fallback for scheduling")
            considerations_lower = considerations.lower()
            
            time_preferences = {
                'morning': (['morning', 'early', 'am'], 8),
                'afternoon': (['afternoon', 'lunch', 'pm'], 12),
                'evening': (['evening', 'night', 'late'], 16)
            }
            
            start_hour = 9
            max_preference_score = 0
            
            for time_of_day, (keywords, hour) in time_preferences.items():
                score = sum(word in considerations_lower for word in keywords)
                if score > max_preference_score:
                    max_preference_score = score
                    start_hour = hour
            
            hours = np.arange(hours_needed)
            slot_hours = (start_hour + hours) % 24
            
            base_probs = np.full(hours_needed, 0.7)
            time_adjustments = {
                'morning': (9, 11, 0.9),
                'afternoon': (14, 16, 0.8),
                'edge': ((0, 7), (20, 24), 0.6)
            }
            
            probs = base_probs.copy()
            for _, (start, end, factor) in time_adjustments.items():
                if isinstance(start, tuple):
                    mask = (slot_hours < start[1]) | (slot_hours > end[0])
                else:
                    mask = (slot_hours >= start) & (slot_hours <= end)
                probs = np.where(mask, factor, probs)
            
            slots = list(zip(slot_hours, probs))
            logger.info("Generated fallback schedule based on time preferences")
        else:
            total_prob = sum(prob for _, prob in optimal_slots[:hours_needed])
            if total_prob > 0:
                slots = [(hour, prob/total_prob) for hour, prob in optimal_slots[:hours_needed]]
            else:
                slots = optimal_slots[:hours_needed]
            logger.info("Generated ML-based optimal schedule")
        
        return slots

    def generate_schedule(self, duration, goals, available_hours, considerations):
        time_slots = self.generate_dynamic_schedule(duration, goals, available_hours, considerations)
        duration_lower = duration.lower()
        
        prompt_methods = {
            'year': self._create_yearly_prompt,
            'month': self._create_monthly_prompt
        }
        
        prompt_method = prompt_methods.get(
            next((key for key in prompt_methods if key in duration_lower), 'week'),
            self._create_weekly_prompt
        )
        
        try:
            prompt = prompt_method(goals, time_slots, considerations)
            response = self.model.generate_content(prompt)
            return self._format_output(response.text, duration, goals, available_hours, considerations, time_slots)
        except Exception as e:
            logger.error(f"Failed to generate schedule: {str(e)}")
            raise ValueError(f"Failed to generate schedule: {e}")

    def _format_slot_time(self, hour):
        return f"{hour:02d}:00"

    def _get_priority(self, hour, slots):
        if slots:
            for slot_hour, prob in slots:
                if slot_hour == hour:
                    if prob >= 0.7:
                        return "HIGH"
                    elif prob >= 0.4:
                        return "MEDIUM"
                    else:
                        return "LOW"
        
        if 9 <= hour <= 11:
            return "HIGH"
        elif 14 <= hour <= 16:
            return "HIGH"
        elif hour < 8 or hour > 20:
            return "LOW"
        else:
            return "MEDIUM"

    def _format_time(self, time_str):
        time_str = time_str.replace(" ", "").upper()
        
        if "AM" in time_str or "PM" in time_str:
            try:
                hour = int(re.search(r'\d+', time_str.split(':')[0]).group())
                if "PM" in time_str and hour != 12:
                    hour += 12
                elif "AM" in time_str and hour == 12:
                    hour = 0
                return f"{hour:02d}:00"
            except Exception as e:
                logger.error(f"Error parsing time string: {str(e)}")
                return time_str
        
        return time_str

    def _format_output(self, schedule, duration, goals, available_hours, considerations, time_slots):
        header = '\n'.join([
            "Schedule Overview",
            "----------------",
            f"Duration: {duration}",
            f"Goals: {goals}",
            f"Hours per day: {available_hours}",
            f"Notes: {considerations}",
            "----------------\n"
        ])

        def process_time_block(line):
            try:
                parts = line.split(':', 1)
                if len(parts) < 2:
                    return line
                    
                time_str = self._format_time(parts[0])
                task = re.sub(r'\s*[\[\(][^)\]]*[\]\)]\s*', '', parts[1]).strip()
                
                try:
                    hour = int(time_str.split(':')[0])
                except ValueError:
                    logger.warning(f"Invalid time format: {time_str}")
                    hour = 9
                    
                priority = self._get_priority(hour, time_slots)
                
                return f"{time_str} - {task} ({priority.capitalize()})"
            except Exception as e:
                logger.error(f"Error processing time block: {str(e)}")
                return line

        days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
        formatted_lines = []
        current_section = None
        
        for line in schedule.strip().split('\n'):
            line = line.strip()
            if not line or "[Continue" in line or "rest" in line.lower():
                continue
                
            if "QUARTER" in line.upper():
                formatted_lines.extend(['', line])
                current_section = "QUARTER"
            elif "WEEK" in line.upper() and "-" in line:
                formatted_lines.extend(['', line.replace('**', '').strip()])
                current_section = "WEEK"
            elif any(day in line.upper() for day in days):
                formatted_lines.extend(['', line.split(':')[0].strip().capitalize()])
                current_section = "DAY"
            elif ':' in line:
                try:
                    formatted_line = process_time_block(line)
                    if formatted_line != line:
                        formatted_lines.append(formatted_line)
                except Exception as e:
                    logger.error(f"Error formatting line: {str(e)}")
                    formatted_lines.append(line)
            elif not any(c in line for c in ['*', '[', ']']):
                formatted_lines.append(line)

        return header + '\n'.join(formatted_lines)

    def _create_weekly_prompt(self, goals, time_slots, considerations):
