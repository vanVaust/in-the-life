import React, { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

interface TreemapNode {
  id: string
  name: string
  value: number
  visual_area: number
  geo_level: string
  children?: TreemapNode[]
}

// FIX 7: D3 HierarchyRectangularNode korrekt typisiert
type RectNode = d3.HierarchyRectangularNode<TreemapNode>

interface Props {
  geoId: string
  width: number
  height: number
  valueField?: string
}

export default function TreemapView({ geoId, width, height, valueField = 'area_km2' }: Props) {
  const svgRef = useRef<SVGSVGElement>(null)

  const { data, isLoading, error } = useQuery<TreemapNode>({
    queryKey: ['treemap', geoId, valueField],
    queryFn: () =>
      api
        .get<TreemapNode>(`/api/v1/treemap/${geoId}?value_field=${valueField}&width=${width}&height=${height}`)
        .then(r => r.data),
  })

  useEffect(() => {
    if (!data || !svgRef.current) return
    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const root = d3
      .hierarchy<TreemapNode>(data)
      .sum(d => d.value)
      .sort((a, b) => (b.value ?? 0) - (a.value ?? 0))

    d3.treemap<TreemapNode>()
      .size([width, height])
      .paddingInner(2)
      .paddingOuter(4)
      .round(true)(root)

    const colorScale = d3.scaleOrdinal<string>(d3.schemeTableau10)

    const cell = svg
      .selectAll<SVGGElement, RectNode>('g')
      .data(root.leaves())
      .join('g')
      .attr('transform', (d: RectNode) => `translate(${d.x0},${d.y0})`)

    cell
      .append('rect')
      .attr('width', (d: RectNode) => Math.max(0, d.x1 - d.x0))
      .attr('height', (d: RectNode) => Math.max(0, d.y1 - d.y0))
      .attr('fill', (d: RectNode) => colorScale(d.data.geo_level))
      .attr('rx', 3)
      .attr('opacity', 0.85)
      .style('cursor', 'pointer')

    cell
      .append('text')
      .attr('x', 4)
      .attr('y', 14)
      .attr('font-size', '11px')
      .attr('fill', '#fff')
      .text((d: RectNode) => {
        const w = d.x1 - d.x0
        return w > 40 ? d.data.name : ''
      })
  }, [data, width, height])

  if (isLoading) return <div style={{ color: '#7dd3fc', padding: 16 }}>Lade Treemap…</div>
  if (error) return <div style={{ color: '#f87171', padding: 16 }}>Fehler beim Laden</div>

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      style={{ background: '#1a1a2e', borderRadius: 8 }}
    />
  )
}
