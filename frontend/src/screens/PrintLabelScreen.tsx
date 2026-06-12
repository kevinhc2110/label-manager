import { useState } from "react";
import {
  ActivityIndicator,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { printLabel } from "../api/labelManager";
import { clearSelectedPrinterId } from "../api/storage";
import { Printer } from "../types/printer";

const ICONS = {
  printer: "🖨️",
  online: "🟢",
  offline: "🔴",
  location: "📍",
  ip: "🌐",
  port: "🔌",
  check: "✅",
  error: "❌",
};

export default function PrintLabelScreen({
  route,
  navigation,
}: {
  route: any;
  navigation: any;
}) {
  const printer: Printer = route.params.printer;
  const insets = useSafeAreaInsets();
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const handlePrint = async () => {
    setStatus("loading");
    setMessage("");
    try {
      const res = await printLabel(printer.id);
      setStatus("success");
      setMessage(res.message);
    } catch (e: any) {
      setStatus("error");
      setMessage(e.message);
    }
  };

  const handleChangePrinter = async () => {
    if (typeof document !== "undefined") {
      (document.activeElement as HTMLElement | null)?.blur();
    }
    await clearSelectedPrinterId();
    navigation.navigate("PrinterList");
  };

  return (
    <View style={{ flex: 1, backgroundColor: "#0f172a", paddingTop: insets.top }}>
      <View
        style={{
          paddingHorizontal: 16,
          paddingVertical: 16,
          flexDirection: "row",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <TouchableOpacity onPress={() => {
          if (typeof document !== "undefined") {
            (document.activeElement as HTMLElement | null)?.blur();
          }
          navigation.goBack();
        }}>
          <Text style={{ color: "#6366f1", fontSize: 18 }}>← Back</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={handleChangePrinter}>
          <Text style={{ color: "#94a3b8", fontSize: 14 }}>Change Printer</Text>
        </TouchableOpacity>
      </View>

      <View style={{ paddingHorizontal: 16, flex: 1 }}>
        <View
          style={{
            backgroundColor: "#1e293b",
            borderRadius: 20,
            padding: 24,
            marginBottom: 24,
            borderWidth: 1,
            borderColor: printer.is_active ? "#22c55e33" : "#334155",
          }}
        >
          <View style={{ alignItems: "center", marginBottom: 16 }}>
            <Text style={{ fontSize: 48, marginBottom: 8 }}>{ICONS.printer}</Text>
            <Text style={{ color: "#f8fafc", fontSize: 24, fontWeight: "700" }}>
              {printer.name}
            </Text>
            <View style={{ flexDirection: "row", alignItems: "center", marginTop: 4 }}>
              <Text style={{ fontSize: 10, marginRight: 4 }}>
                {printer.is_active ? ICONS.online : ICONS.offline}
              </Text>
              <Text style={{ color: "#94a3b8", fontSize: 14 }}>
                {printer.is_active ? "Online" : "Offline"}
              </Text>
            </View>
          </View>

          <View style={{ gap: 12 }}>
            <InfoRow icon={ICONS.location} label="Location" value={printer.location} />
            <InfoRow icon={ICONS.ip} label="IP Address" value={printer.ip_address} />
            <InfoRow icon={ICONS.port} label="Port" value={String(printer.port)} />
          </View>
        </View>

        <TouchableOpacity
          activeOpacity={0.8}
          onPress={handlePrint}
          disabled={status === "loading"}
          style={{
            backgroundColor: status === "loading" ? "#4f46e5" : "#6366f1",
            borderRadius: 16,
            padding: 18,
            alignItems: "center",
            opacity: status === "loading" ? 0.7 : 1,
          }}
        >
          {status === "loading" ? (
            <ActivityIndicator color="#f8fafc" />
          ) : (
            <Text style={{ color: "#f8fafc", fontSize: 18, fontWeight: "700" }}>
              Print Label
            </Text>
          )}
        </TouchableOpacity>

        {status === "success" && (
          <View
            style={{
              backgroundColor: "#064e3b",
              borderRadius: 12,
              padding: 16,
              marginTop: 16,
              flexDirection: "row",
              alignItems: "center",
              gap: 8,
            }}
          >
            <Text style={{ fontSize: 18 }}>{ICONS.check}</Text>
            <Text style={{ color: "#bbf7d0", fontSize: 15, flex: 1 }}>{message}</Text>
          </View>
        )}

        {status === "error" && (
          <View
            style={{
              backgroundColor: "#450a0a",
              borderRadius: 12,
              padding: 16,
              marginTop: 16,
              flexDirection: "row",
              alignItems: "center",
              gap: 8,
            }}
          >
            <Text style={{ fontSize: 18 }}>{ICONS.error}</Text>
            <Text style={{ color: "#fecaca", fontSize: 15, flex: 1 }}>{message}</Text>
          </View>
        )}
      </View>
    </View>
  );
}

function InfoRow({
  icon,
  label,
  value,
}: {
  icon: string;
  label: string;
  value: string;
}) {
  return (
    <View style={{ flexDirection: "row", alignItems: "center" }}>
      <Text style={{ fontSize: 16, marginRight: 8, width: 24, textAlign: "center" }}>
        {icon}
      </Text>
      <Text style={{ color: "#64748b", fontSize: 14, width: 80 }}>{label}</Text>
      <Text style={{ color: "#f8fafc", fontSize: 14, fontWeight: "500" }}>{value}</Text>
    </View>
  );
}
