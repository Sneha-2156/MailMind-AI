import { describe, it, expect } from 'vitest'
import {
  formatCategory,
  formatPriority,
  formatOpportunityType,
  formatStatus,
  formatSenderInitials,
} from './format'

describe('Format Utility Functions', () => {
  it('formats categories properly', () => {
    expect(formatCategory('Academic')).toBe('Academic')
    expect(formatCategory(null)).toBe('Uncategorized')
    expect(formatCategory('')).toBe('Uncategorized')
  })

  it('formats priority strings with proper casing', () => {
    expect(formatPriority('critical')).toBe('Critical')
    expect(formatPriority('high')).toBe('High')
    expect(formatPriority(null)).toBe('Normal')
  })

  it('formats opportunity types accurately', () => {
    expect(formatOpportunityType('internship')).toBe('Internship')
    expect(formatOpportunityType('job')).toBe('Full-time Job')
    expect(formatOpportunityType('hackathon')).toBe('Hackathon')
    expect(formatOpportunityType(null)).toBe('Opportunity')
  })

  it('maps opportunity statuses correctly', () => {
    expect(formatStatus('new')).toBe('New')
    expect(formatStatus('offer')).toBe('Offer Received')
    expect(formatStatus('rejected')).toBe('Archived')
    expect(formatStatus(null)).toBe('New')
  })

  it('generates sender initials correctly', () => {
    expect(formatSenderInitials('Alex Morgan', 'alex@example.com')).toBe('AM')
    expect(formatSenderInitials(null, 'john.doe@domain.com')).toBe('JO')
  })
})
