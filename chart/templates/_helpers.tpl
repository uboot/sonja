{{/*
Expand the name of the chart.
*/}}
{{- define "conan-ci.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "conan-ci.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "conan-ci.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "conan-ci.labels" -}}
helm.sh/chart: {{ include "conan-ci.chart" . }}
{{ include "conan-ci.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "conan-ci.selectorLabels" -}}
app.kubernetes.io/name: {{ include "conan-ci.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "conan-ci.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "conan-ci.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create a daemon.json for Docker for Windows
*/}}
{{- define "conan-ci.daemonJson" -}}
{
    "hosts": ["tcp://0.0.0.0:2375", "npipe://"],
    "insecure-registries": {{ $.Values.insecureRegistries | toJson }},
    "mtu": {{ .Values.mtu | default 1500 }}
}
{{- end }}

{{/*
Create a Base64 encoded daemon.json for Docker for Windows
*/}}
{{- define "conan-ci.daemonJsonB64" -}}
{{ include "conan-ci.daemonJson" . | b64enc }}
{{- end }}
