export const trackEvent = (eventName: string, properties?: Record<string, any>) => {
  if (typeof window !== 'undefined' && (window as any).gtag) {
    (window as any).gtag('event', eventName, properties || {});
  }
  console.log(`📊 Event: ${eventName}`, properties);
};

export const analytics = {
  signup: (email: string) => trackEvent('signup', { email }),
  login: (email: string) => trackEvent('login', { email }),
  jobSearch: (query: string) => trackEvent('job_search', { query }),
  applyJob: (jobId: string) => trackEvent('apply_job', { jobId }),
  saveJob: (jobId: string) => trackEvent('save_job', { jobId }),
};
