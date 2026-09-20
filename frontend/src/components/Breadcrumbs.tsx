import { Box, Breadcrumbs as MuiBreadcrumbs, Link, Typography } from '@mui/material';
import { NavigateNext as NavigateNextIcon, Home as HomeIcon } from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

interface BreadcrumbItem {
  label: string;
  path?: string;
  icon?: React.ReactNode;
}

interface BreadcrumbsProps {
  items?: BreadcrumbItem[];
}

export default function Breadcrumbs({ items }: BreadcrumbsProps) {
  const navigate = useNavigate();
  const location = useLocation();

  // Auto-generate breadcrumbs from path if not provided
  const breadcrumbItems = items || generateBreadcrumbsFromPath(location.pathname);

  return (
    <Box sx={{ mb: 2 }}>
      <MuiBreadcrumbs
        separator={<NavigateNextIcon fontSize="small" />}
        aria-label="breadcrumb"
        sx={{
          '& .MuiBreadcrumbs-separator': {
            mx: 0.5,
          },
        }}
      >
        {breadcrumbItems.map((item, index) => {
          const isLast = index === breadcrumbItems.length - 1;

          if (isLast) {
            return (
              <Typography
                key={item.path || index}
                color="text.primary"
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  fontWeight: 600,
                }}
              >
                {item.icon && (
                  <Box component="span" sx={{ mr: 0.5, display: 'flex' }}>
                    {item.icon}
                  </Box>
                )}
                {item.label}
              </Typography>
            );
          }

          return (
            <Link
              key={item.path || index}
              color="inherit"
              onClick={() => item.path && navigate(item.path)}
              sx={{
                display: 'flex',
                alignItems: 'center',
                cursor: 'pointer',
                textDecoration: 'none',
                '&:hover': {
                  textDecoration: 'underline',
                },
              }}
            >
              {item.icon && (
                <Box component="span" sx={{ mr: 0.5, display: 'flex' }}>
                  {item.icon}
                </Box>
              )}
              {item.label}
            </Link>
          );
        })}
      </MuiBreadcrumbs>
    </Box>
  );
}

// Auto-generate breadcrumbs from URL path
function generateBreadcrumbsFromPath(pathname: string): BreadcrumbItem[] {
  const paths = pathname.split('/').filter(Boolean);
  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Home', path: '/dashboard', icon: <HomeIcon fontSize="small" /> },
  ];

  let currentPath = '';
  paths.forEach((segment, index) => {
    currentPath += `/${segment}`;

    // Skip if it's an ID (number)
    if (!isNaN(Number(segment))) {
      return;
    }

    // Convert path segment to readable label
    const label = segment
      .split('-')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');

    breadcrumbs.push({
      label,
      path: index === paths.length - 1 ? undefined : currentPath,
    });
  });

  return breadcrumbs;
}
