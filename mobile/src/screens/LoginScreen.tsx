import React, { useState } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { TextInput, Button, Text, Card } from 'react-native-paper';
import { useAuth } from '../contexts/AuthContext';

export default function LoginScreen({ navigation }: any) {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!username || !password) {
      Alert.alert('Error', 'Please enter username and password');
      return;
    }
    setLoading(true);
    try {
      await login(username, password);
      navigation.replace('Dashboard');
    } catch (e: any) {
      Alert.alert('Login Failed', e.response?.data?.detail || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="headlineMedium" style={styles.title}>SuperDev AI Suite</Text>
          <Text variant="bodyMedium" style={styles.subtitle}>Sign in to your account</Text>
          <TextInput label="Username" value={username} onChangeText={setUsername} mode="outlined" style={styles.input} />
          <TextInput label="Password" value={password} onChangeText={setPassword} mode="outlined" secureTextEntry style={styles.input} />
          <Button mode="contained" onPress={handleLogin} loading={loading} style={styles.button}>Sign In</Button>
          <Text variant="bodySmall" style={styles.hint}>Demo: admin / admin123</Text>
        </Card.Content>
      </Card>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 20, backgroundColor: '#f5f5f5' },
  card: { padding: 10 },
  title: { textAlign: 'center', marginBottom: 8, fontWeight: 'bold' },
  subtitle: { textAlign: 'center', marginBottom: 24, color: '#666' },
  input: { marginBottom: 12 },
  button: { marginTop: 8, paddingVertical: 4 },
  hint: { textAlign: 'center', marginTop: 12, color: '#999' },
});
