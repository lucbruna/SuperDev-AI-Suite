import React, { useEffect, useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Card, Text, Button, Chip } from 'react-native-paper';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../api/client';

export default function DashboardScreen({ navigation }: any) {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState({ users: 0, scans: 0, aiQueries: 0 });

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [usersRes, scansRes] = await Promise.all([
        apiClient.get('/api/users?size=1').catch(() => ({ data: { total: 0 } })),
        apiClient.get('/api/scanners/history?size=1').catch(() => ({ data: { total: 0 } })),
      ]);
      setStats({
        users: usersRes.data?.total || 0,
        scans: scansRes.data?.total || 0,
        aiQueries: 0,
      });
    } catch {}
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.welcomeCard}>
        <Card.Content>
          <Text variant="headlineSmall">Welcome, {user?.full_name || user?.username || 'User'}</Text>
          <Chip style={styles.roleChip}>{user?.role || 'user'}</Chip>
        </Card.Content>
      </Card>

      <View style={styles.statsRow}>
        <Card style={styles.statCard}>
          <Card.Content style={styles.statContent}>
            <Text variant="headlineMedium">{stats.users}</Text>
            <Text variant="bodySmall">Users</Text>
          </Card.Content>
        </Card>
        <Card style={styles.statCard}>
          <Card.Content style={styles.statContent}>
            <Text variant="headlineMedium">{stats.scans}</Text>
            <Text variant="bodySmall">Scans</Text>
          </Card.Content>
        </Card>
        <Card style={styles.statCard}>
          <Card.Content style={styles.statContent}>
            <Text variant="headlineMedium">{stats.aiQueries}</Text>
            <Text variant="bodySmall">AI Queries</Text>
          </Card.Content>
        </Card>
      </View>

      <Card style={styles.actionCard}>
        <Card.Content>
          <Text variant="titleMedium" style={styles.sectionTitle}>Quick Actions</Text>
          <Button mode="outlined" icon="shield-check" onPress={() => navigation.navigate('Scanner')} style={styles.actionBtn}>Security Scanner</Button>
          <Button mode="outlined" icon="robot" onPress={() => navigation.navigate('AIAssistant')} style={styles.actionBtn}>AI Assistant</Button>
          <Button mode="outlined" icon="logout" onPress={logout} style={styles.actionBtn}>Logout</Button>
        </Card.Content>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5', padding: 16 },
  welcomeCard: { marginBottom: 16 },
  roleChip: { marginTop: 8, alignSelf: 'flex-start' },
  statsRow: { flexDirection: 'row', gap: 8, marginBottom: 16 },
  statCard: { flex: 1 },
  statContent: { alignItems: 'center', paddingVertical: 8 },
  actionCard: { marginBottom: 16 },
  sectionTitle: { marginBottom: 12, fontWeight: 'bold' },
  actionBtn: { marginBottom: 8 },
});
