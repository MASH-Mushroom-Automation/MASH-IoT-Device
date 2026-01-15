"""
Device Creation Web Server
Standalone Flask server for device creation and management
Communicates with MASH Backend API
"""

import os
import sys
import logging
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.device_id_generator import DeviceIDGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../../templates',
            static_folder='../../templates')
CORS(app)

# Backend configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'https://mash-backend-production.up.railway.app')
BACKEND_API_URL = f"{BACKEND_URL}/api/v1"

logger.info(f"Backend API URL: {BACKEND_API_URL}")


@app.route('/')
def index():
    """Serve the device creation page"""
    return render_template('device_creation.html')


@app.route('/api/v1/device-id/generate', methods=['POST'])
def generate_device_id():
    """Generate a new device ID with Luhn checksum"""
    try:
        data = request.json or {}
        
        brand = data.get('brand', 'MASH')
        model = data.get('model', 'A')
        version = data.get('version', 1)
        location = data.get('location', 'CAL')
        year = data.get('year', 25)
        
        # Generate device ID
        device_id, components = DeviceIDGenerator.generate_device_id(
            brand=brand,
            model=model,
            version=version,
            location=location,
            year=year
        )
        
        logger.info(f"Generated device ID: {device_id}")
        
        return jsonify({
            'success': True,
            'device_id': device_id,
            'components': components,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating device ID: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/v1/device-id/validate', methods=['POST'])
def validate_device_id():
    """Validate a device ID"""
    try:
        data = request.json or {}
        device_id = data.get('device_id', '')
        
        if not device_id:
            return jsonify({
                'success': False,
                'message': 'Device ID is required'
            }), 400
        
        # Validate device ID
        is_valid = DeviceIDGenerator.validate_device_id(device_id)
        parsed = DeviceIDGenerator.parse_device_id(device_id)
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'parsed': parsed
        })
        
    except Exception as e:
        logger.error(f"Error validating device ID: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/v1/devices', methods=['GET'])
def list_devices():
    """List all devices with pagination and filters - proxies to backend"""
    try:
        # Get query parameters
        params = {
            'page': request.args.get('page', 1, type=int),
            'perPage': request.args.get('perPage', 30, type=int),
        }
        
        if request.args.get('status'):
            params['status'] = request.args.get('status')
        if request.args.get('isActive'):
            params['isActive'] = request.args.get('isActive')
        
        # Make request to backend
        response = requests.get(
            f"{BACKEND_API_URL}/devices",
            params=params,
            timeout=10
        )
        
        if response.ok:
            data = response.json()
            # Ensure the response has the expected structure
            if 'data' in data:
                return jsonify(data)
            else:
                # Wrap response if needed
                return jsonify({
                    'success': True,
                    'data': {
                        'devices': data if isinstance(data, list) else [],
                        'pagination': {
                            'page': params['page'],
                            'perPage': params['perPage'],
                            'total': len(data) if isinstance(data, list) else 0,
                            'totalPages': 1
                        }
                    }
                })
        else:
            logger.error(f"Backend error: {response.status_code} - {response.text}")
            return jsonify({
                'success': False,
                'message': f'Backend error: {response.status_code}'
            }), response.status_code
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to backend: {e}")
        return jsonify({
            'success': False,
            'message': f'Cannot connect to backend: {str(e)}',
            'data': {
                'devices': [],
                'pagination': {
                    'page': 1,
                    'perPage': 30,
                    'total': 0,
                    'totalPages': 0
                }
            }
        }), 503
    except Exception as e:
        logger.error(f"Error listing devices: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/v1/devices', methods=['POST'])
def create_device():
    """Create a new device - proxies to backend"""
    try:
        data = request.json or {}
        
        # Validate required fields
        required_fields = ['id', 'name', 'type', 'serialNumber']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        logger.info(f"Creating device: {data['id']}")
        
        # Make request to backend
        response = requests.post(
            f"{BACKEND_API_URL}/devices",
            json=data,
            timeout=10
        )
        
        if response.ok:
            logger.info(f"Device created successfully: {data['id']}")
            return jsonify(response.json()), response.status_code
        else:
            logger.error(f"Backend error: {response.status_code} - {response.text}")
            return jsonify({
                'success': False,
                'message': f'Backend error: {response.text}'
            }), response.status_code
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to backend: {e}")
        return jsonify({
            'success': False,
            'message': f'Cannot connect to backend: {str(e)}'
        }), 503
    except Exception as e:
        logger.error(f"Error creating device: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/v1/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    """Get device details by ID"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM device WHERE id = ?", (device_id,))
            row = cursor.fetchone()
        
            if not row:
                return jsonify({
                    'success': False,
                    'message': 'Device not found'
                }), 404
            
            device = {
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'serialNumber': row[3],
                'status': row[4],
                'userId': row[5],
                'location': row[6],
                'description': row[7],
                'firmware': row[8],
                'ipAddress': row[9],
                'macAddress': row[10],
                'lastSeen': row[11],
                'isActive': bool(row[12]),
                'createdAt': row[13],
                'updatedAt': row[14]
            }
            
            return jsonify({
                'success': True,
                'data': device
            })
        
    except Exception as e:
        logger.error(f"Error getting device: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/v1/devices/<device_id>', methods=['PUT'])
def update_device(device_id):
    """Update device information"""
    try:
        data = request.json or {}
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
        
            # Build update query
            updates = []
            params = []
            
            for field in ['name', 'type', 'status', 'userId', 'location', 'description', 
                         'firmware', 'ipAddress', 'macAddress', 'isActive']:
                if field in data:
                    updates.append(f"{field} = ?")
                    if field == 'isActive':
                        params.append(1 if data[field] else 0)
                    else:
                        params.append(data[field])
            
            if not updates:
                return jsonify({
                    'success': False,
                    'message': 'No fields to update'
                }), 400
            
            # Add updatedAt
            updates.append("updatedAt = ?")
            params.append(datetime.now().isoformat())
            
            # Add device_id to params
            params.append(device_id)
            
            # Execute update
            query = f"UPDATE device SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            
            if cursor.rowcount == 0:
                return jsonify({
                    'success': False,
                    'message': 'Device not found'
                }), 404
            
            conn.commit()
            
            logger.info(f"Updated device: {device_id}")
        
        return jsonify({
            'success': True,
            'message': 'Device updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating device: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/v1/devices/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    """Soft delete device - proxies to backend"""
    try:
        logger.info(f"Deleting device: {device_id}")
        
        response = requests.delete(
            f"{BACKEND_API_URL}/devices/{device_id}",
            timeout=10
        )
        
        if response.ok:
            logger.info(f"Device deleted successfully: {device_id}")
            return jsonify({
                'success': True,
                'message': 'Device deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Device not found' if response.status_code == 404 else f'Backend error: {response.status_code}'
            }), response.status_code
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to backend: {e}")
        return jsonify({
            'success': False,
            'message': f'Cannot connect to backend: {str(e)}'
        }), 503
    except Exception as e:
        logger.error(f"Error deleting device: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/v1/devices/<device_id>/activate', methods=['POST'])
def activate_device(device_id):
    """Activate or deactivate device - proxies to backend"""
    try:
        data = request.json or {}
        is_active = data.get('isActive', True)
        
        logger.info(f"{'Activating' if is_active else 'Deactivating'} device: {device_id}")
        
        response = requests.post(
            f"{BACKEND_API_URL}/devices/{device_id}/activate",
            json=data,
            timeout=10
        )
        
        if response.ok:
            logger.info(f"Device {'activated' if is_active else 'deactivated'} successfully: {device_id}")
            return jsonify(response.json())
        else:
            return jsonify({
                'success': False,
                'message': 'Device not found' if response.status_code == 404 else f'Backend error: {response.status_code}'
            }), response.status_code
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to backend: {e}")
        return jsonify({
            'success': False,
            'message': f'Cannot connect to backend: {str(e)}'
        }), 503
    except Exception as e:
        logger.error(f"Error activating device: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'MASH Device Creation Server'
    })


if __name__ == '__main__':
    logger.info("Starting MASH Device Creation Server...")
    logger.info(f"Backend API: {BACKEND_API_URL}")
    
    # Run server
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
