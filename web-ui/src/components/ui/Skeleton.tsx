import { motion } from 'framer-motion';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  count?: number;
}

export function Skeleton({
  className = '',
  variant = 'rectangular',
  width,
  height,
  count = 1
}: SkeletonProps) {
  const baseClasses = 'bg-gray-800 overflow-hidden relative';

  const variantClasses = {
    text: 'rounded h-4',
    circular: 'rounded-full',
    rectangular: 'rounded-lg'
  };

  const style = {
    width: width || '100%',
    height: height || (variant === 'text' ? '1rem' : '100%')
  };

  const skeletons = Array.from({ length: count }, (_, i) => (
    <div
      key={i}
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      style={style}
    >
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-gray-700 to-transparent"
        animate={{
          x: ['-100%', '100%']
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: 'linear'
        }}
      />
    </div>
  ));

  return count === 1 ? skeletons[0] : <div className="space-y-2">{skeletons}</div>;
}

// Pre-built skeleton components for common use cases
export function CardSkeleton() {
  return (
    <div className="bg-gray-900/50 rounded-xl p-6 border border-gray-800">
      <Skeleton variant="text" width="60%" className="mb-4" />
      <Skeleton variant="text" count={3} className="mb-2" />
      <div className="flex gap-4 mt-4">
        <Skeleton variant="rectangular" width={80} height={32} />
        <Skeleton variant="rectangular" width={80} height={32} />
      </div>
    </div>
  );
}

export function StatsSkeleton() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="bg-gray-900/50 rounded-xl p-4 border border-gray-800">
          <Skeleton variant="text" width="50%" height={12} className="mb-2" />
          <Skeleton variant="text" width="80%" height={24} />
        </div>
      ))}
    </div>
  );
}

export function PuzzleSkeleton() {
  return (
    <div className="space-y-6">
      <div className="bg-gray-900/50 rounded-xl p-6 border border-gray-800">
        <Skeleton variant="text" width="40%" height={28} className="mb-4" />
        <Skeleton variant="text" count={2} className="mb-4" />
        <div className="flex gap-2">
          <Skeleton variant="rectangular" width={60} height={24} className="rounded-full" />
          <Skeleton variant="rectangular" width={80} height={24} className="rounded-full" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[...Array(4)].map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
    </div>
  );
}

export function PortfolioSkeleton() {
  return (
    <div className="space-y-6">
      <StatsSkeleton />
      <div className="bg-gray-900/50 rounded-xl p-6 border border-gray-800">
        <Skeleton variant="text" width="30%" className="mb-4" />
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex items-center justify-between py-2">
              <div className="flex items-center gap-3">
                <Skeleton variant="circular" width={40} height={40} />
                <div>
                  <Skeleton variant="text" width={100} height={16} className="mb-1" />
                  <Skeleton variant="text" width={60} height={12} />
                </div>
              </div>
              <Skeleton variant="text" width={80} height={20} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function DashboardSkeleton() {
  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Skeleton variant="text" width={200} height={32} className="mb-2" />
          <Skeleton variant="text" width={150} height={16} />
        </div>
        <Skeleton variant="circular" width={48} height={48} />
      </div>

      {/* Stats */}
      <StatsSkeleton />

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CardSkeleton />
        <CardSkeleton />
      </div>
    </div>
  );
}
